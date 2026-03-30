"""
Automated test suite for PawPal+ (pawpal_system.py).

Covers:
  - Task completion and status flag
  - Recurring task auto-generation (daily and weekly)
  - One-off task produces no next occurrence
  - Priority scoring
  - Pet task management
  - Scheduler: sort_by_time (happy path + untimed tasks)
  - Scheduler: filter_by_status and filter_by_pet
  - Scheduler: conflict detection (overlap, exact same time, no conflict)
  - Scheduler: generate_schedule respects time budget
  - Edge cases: pet with no tasks, all tasks over budget
"""

import sys
import os
from datetime import date, timedelta

# Allow running from the repo root or from the tests/ directory.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet, Owner, Scheduler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_scheduler(available_minutes=120):
    owner = Owner("Jordan", "", available_minutes)
    pet = Pet("Mochi", "dog", 3)
    owner.add_pet(pet)
    return Scheduler(owner, pet), pet


# ---------------------------------------------------------------------------
# Task: completion and status
# ---------------------------------------------------------------------------

def test_mark_complete():
    task = Task("Feed Dog", 10, "medium", "feeding", "morning", False)
    task.mark_complete()
    assert task.is_completed is True


def test_one_off_task_returns_no_next_occurrence():
    task = Task("Vet visit", 60, "high")
    next_task = task.mark_complete()
    assert next_task is None


# ---------------------------------------------------------------------------
# Task: recurring — daily
# ---------------------------------------------------------------------------

def test_daily_task_creates_next_occurrence():
    today = date(2026, 3, 29)
    task = Task("Morning walk", 20, "high", frequency="daily", due_date=today)
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)


def test_daily_task_preserves_attributes():
    today = date(2026, 3, 29)
    task = Task("Morning walk", 20, "high", start_time="08:00",
                frequency="daily", pet_name="Mochi", due_date=today)
    next_task = task.mark_complete()
    assert next_task.title == "Morning walk"
    assert next_task.duration_minutes == 20
    assert next_task.start_time == "08:00"
    assert next_task.frequency == "daily"
    assert next_task.is_completed is False   # next occurrence starts fresh


def test_daily_task_without_due_date_uses_today():
    task = Task("Walk", 20, "high", frequency="daily")
    next_task = task.mark_complete()
    assert next_task.due_date == date.today() + timedelta(days=1)


# ---------------------------------------------------------------------------
# Task: recurring — weekly
# ---------------------------------------------------------------------------

def test_weekly_task_creates_next_occurrence():
    today = date(2026, 3, 29)
    task = Task("Grooming", 45, "medium", frequency="weekly", due_date=today)
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)


# ---------------------------------------------------------------------------
# Task: priority scoring
# ---------------------------------------------------------------------------

def test_priority_scores():
    assert Task("a", 5, "high").get_priority_score() == 3
    assert Task("b", 5, "medium").get_priority_score() == 2
    assert Task("c", 5, "low").get_priority_score() == 1
    assert Task("d", 5, "unknown").get_priority_score() == 0


# ---------------------------------------------------------------------------
# Pet: task management
# ---------------------------------------------------------------------------

def test_add_task_to_pet():
    pet = Pet("Buddy", "Dog", 3, [], [])
    task = Task("Walk", 20, "high", "exercise", "evening", False)
    pet.add_task(task)
    assert len(pet.assigned_tasks) == 1


def test_get_tasks_by_priority_order():
    pet = Pet("Buddy", "dog", 2)
    low  = Task("Play",  10, "low")
    high = Task("Meds",   5, "high")
    mid  = Task("Feed",  15, "medium")
    for t in [low, high, mid]:
        pet.add_task(t)
    ordered = pet.get_tasks_by_priority()
    assert ordered[0].priority == "high"
    assert ordered[1].priority == "medium"
    assert ordered[2].priority == "low"


def test_pet_with_no_tasks_returns_empty_priority_list():
    pet = Pet("Ghost", "cat", 1)
    assert pet.get_tasks_by_priority() == []


# ---------------------------------------------------------------------------
# Scheduler: sort_by_time
# ---------------------------------------------------------------------------

def test_sort_by_time_chronological():
    scheduler, _ = make_scheduler()
    tasks = [
        Task("Evening walk",  20, "high",   start_time="18:00"),
        Task("Morning feed",  10, "medium", start_time="07:30"),
        Task("Midday meds",    5, "high",   start_time="12:00"),
    ]
    result = scheduler.sort_by_time(tasks)
    assert [t.start_time for t in result] == ["07:30", "12:00", "18:00"]


def test_sort_by_time_untimed_tasks_go_last():
    scheduler, _ = make_scheduler()
    tasks = [
        Task("No time",   10, "low",  start_time=""),
        Task("Timed",     10, "high", start_time="09:00"),
    ]
    result = scheduler.sort_by_time(tasks)
    assert result[0].start_time == "09:00"
    assert result[1].start_time == ""


def test_sort_by_time_empty_list():
    scheduler, _ = make_scheduler()
    assert scheduler.sort_by_time([]) == []


# ---------------------------------------------------------------------------
# Scheduler: filtering
# ---------------------------------------------------------------------------

def test_filter_by_status_pending():
    scheduler, _ = make_scheduler()
    done    = Task("Done task",    10, "low",  is_completed=True)
    pending = Task("Pending task", 10, "high", is_completed=False)
    result = scheduler.filter_by_status([done, pending], completed=False)
    assert len(result) == 1
    assert result[0].title == "Pending task"


def test_filter_by_status_completed():
    scheduler, _ = make_scheduler()
    done    = Task("Done",    10, "low",  is_completed=True)
    pending = Task("Pending", 10, "high", is_completed=False)
    result = scheduler.filter_by_status([done, pending], completed=True)
    assert len(result) == 1
    assert result[0].title == "Done"


def test_filter_by_pet_correct_pet():
    scheduler, _ = make_scheduler()
    mochi = Task("Walk",  20, "high",   pet_name="Mochi")
    buddy = Task("Fetch", 15, "medium", pet_name="Buddy")
    result = scheduler.filter_by_pet([mochi, buddy], "Mochi")
    assert len(result) == 1
    assert result[0].pet_name == "Mochi"


def test_filter_by_pet_no_match_returns_empty():
    scheduler, _ = make_scheduler()
    tasks = [Task("Walk", 20, "high", pet_name="Buddy")]
    assert scheduler.filter_by_pet(tasks, "Mochi") == []


# ---------------------------------------------------------------------------
# Scheduler: conflict detection
# ---------------------------------------------------------------------------

def test_detect_no_conflicts():
    scheduler, _ = make_scheduler()
    tasks = [
        Task("Walk",  30, "high", start_time="08:00"),
        Task("Meds",   5, "high", start_time="09:00"),
    ]
    assert scheduler.detect_conflicts(tasks) == []


def test_detect_overlap_conflict():
    scheduler, _ = make_scheduler()
    # Walk: 08:00–08:30, Feed: 08:15–08:25  → overlap
    tasks = [
        Task("Walk", 30, "high",   start_time="08:00"),
        Task("Feed", 10, "medium", start_time="08:15"),
    ]
    warnings = scheduler.detect_conflicts(tasks)
    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Feed" in warnings[0]


def test_detect_exact_same_start_time():
    scheduler, _ = make_scheduler()
    tasks = [
        Task("Task A", 20, "high",   start_time="09:00"),
        Task("Task B", 15, "medium", start_time="09:00"),
    ]
    warnings = scheduler.detect_conflicts(tasks)
    assert len(warnings) == 1


def test_detect_conflicts_skips_untimed_tasks():
    scheduler, _ = make_scheduler()
    tasks = [
        Task("No time A", 60, "high"),
        Task("No time B", 60, "medium"),
    ]
    assert scheduler.detect_conflicts(tasks) == []


# ---------------------------------------------------------------------------
# Scheduler: generate_schedule
# ---------------------------------------------------------------------------

def test_generate_schedule_respects_time_budget():
    scheduler, pet = make_scheduler(available_minutes=30)
    pet.add_task(Task("Walk",     20, "high"))
    pet.add_task(Task("Grooming", 30, "medium"))  # won't fit after Walk
    scheduled = scheduler.generate_schedule()
    assert len(scheduled) == 1
    assert scheduled[0].title == "Walk"
    assert scheduler.total_minutes_used == 20


def test_generate_schedule_priority_order():
    scheduler, pet = make_scheduler(available_minutes=60)
    pet.add_task(Task("Low task",  10, "low"))
    pet.add_task(Task("High task", 10, "high"))
    scheduled = scheduler.generate_schedule()
    assert scheduled[0].title == "High task"


def test_generate_schedule_pet_with_no_tasks():
    scheduler, _ = make_scheduler()
    scheduled = scheduler.generate_schedule()
    assert scheduled == []
    assert scheduler.explain_plan() == "No tasks scheduled."


def test_generate_schedule_all_tasks_over_budget():
    scheduler, pet = make_scheduler(available_minutes=10)
    pet.add_task(Task("Big task", 60, "high"))
    scheduled = scheduler.generate_schedule()
    assert scheduled == []


# ---------------------------------------------------------------------------
# Scheduler: mark_task_complete with recurrence
# ---------------------------------------------------------------------------

def test_mark_task_complete_adds_next_occurrence():
    scheduler, pet = make_scheduler()
    today = date(2026, 3, 29)
    task = Task("Walk", 20, "high", frequency="daily",
                pet_name="Mochi", due_date=today)
    scheduler.add_task(task)
    initial_count = len(pet.assigned_tasks)
    scheduler.mark_task_complete(task)
    assert len(pet.assigned_tasks) == initial_count + 1
    assert pet.assigned_tasks[-1].due_date == today + timedelta(days=1)


def test_mark_task_complete_one_off_does_not_add_task():
    scheduler, pet = make_scheduler()
    task = Task("Vet visit", 60, "high", pet_name="Mochi")
    scheduler.add_task(task)
    initial_count = len(pet.assigned_tasks)
    scheduler.mark_task_complete(task)
    assert len(pet.assigned_tasks) == initial_count  # no new task added
