from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str           # "low", "medium", "high"
    category: str = ""
    time_of_day: str = ""   # "morning", "afternoon", "evening", or ""
    start_time: str = ""    # "HH:MM" format, e.g. "08:30"
    frequency: str = ""     # "daily", "weekly", or "" for one-off
    pet_name: str = ""      # which pet this task belongs to
    due_date: Optional[date] = None
    is_completed: bool = False

    def get_priority_score(self) -> int:
        """Return a numeric score for the task's priority level."""
        return {"low": 1, "medium": 2, "high": 3}.get(self.priority, 0)

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task as completed and return the next occurrence if recurring."""
        self.is_completed = True
        if self.frequency == "daily":
            next_due = (self.due_date or date.today()) + timedelta(days=1)
            return Task(
                title=self.title,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                category=self.category,
                time_of_day=self.time_of_day,
                start_time=self.start_time,
                frequency=self.frequency,
                pet_name=self.pet_name,
                due_date=next_due,
            )
        if self.frequency == "weekly":
            next_due = (self.due_date or date.today()) + timedelta(weeks=1)
            return Task(
                title=self.title,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                category=self.category,
                time_of_day=self.time_of_day,
                start_time=self.start_time,
                frequency=self.frequency,
                pet_name=self.pet_name,
                due_date=next_due,
            )
        return None  # one-off task: no next occurrence


@dataclass
class Pet:
    name: str
    species: str
    age: int
    preferences: List[str] = field(default_factory=list)
    assigned_tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's assigned task list."""
        self.assigned_tasks.append(task)

    def get_tasks_by_priority(self) -> List[Task]:
        """Return assigned tasks sorted from highest to lowest priority."""
        return sorted(self.assigned_tasks, key=lambda t: t.get_priority_score(), reverse=True)


class Owner:
    def __init__(self, name: str, email: str, available_minutes_per_day: int):
        self.name = name
        self.email = email
        self.available_minutes_per_day = available_minutes_per_day
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def get_total_available_time(self) -> int:
        """Return the owner's total available minutes for pet care today."""
        return self.available_minutes_per_day


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.scheduled_tasks: List[Task] = []
        self.total_minutes_used: int = 0

    def add_task(self, task: Task) -> None:
        """Register a task with the pet for later scheduling."""
        self.pet.add_task(task)

    def generate_schedule(self) -> List[Task]:
        """Build a greedy daily schedule ordered by priority within the time budget."""
        self.scheduled_tasks = []
        self.total_minutes_used = 0
        for task in self._sort_by_priority(self.pet.assigned_tasks):
            if self._fits_in_day(task):
                self.scheduled_tasks.append(task)
                self.total_minutes_used += task.duration_minutes
        return self.scheduled_tasks

    # ------------------------------------------------------------------
    # Step 2: Sorting by start time
    # ------------------------------------------------------------------

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks sorted by start_time in ascending HH:MM order.

        Compares times lexicographically, which is safe for zero-padded
        "HH:MM" strings (e.g. "08:00" < "09:30"). Tasks that have no
        start_time are placed at the end of the list.

        Args:
            tasks: Any list of Task objects to sort.

        Returns:
            A new list sorted by start_time ascending; untimed tasks last.
        """
        def time_key(t: Task) -> str:
            # Tasks with no start_time sort after all timed tasks.
            return t.start_time if t.start_time else "99:99"

        return sorted(tasks, key=time_key)

    # ------------------------------------------------------------------
    # Step 2: Filtering
    # ------------------------------------------------------------------

    def filter_by_status(self, tasks: List[Task], completed: bool) -> List[Task]:
        """Return only tasks whose completion status matches the given flag.

        Args:
            tasks: The list of Task objects to filter.
            completed: Pass True to get only completed tasks,
                       False to get only pending tasks.

        Returns:
            A filtered list containing tasks where is_completed == completed.
        """
        return [t for t in tasks if t.is_completed == completed]

    def filter_by_pet(self, tasks: List[Task], pet_name: str) -> List[Task]:
        """Return only tasks assigned to the named pet.

        Matches against Task.pet_name using an exact, case-sensitive
        comparison.

        Args:
            tasks: The list of Task objects to filter.
            pet_name: The pet's name to match (e.g. "Mochi").

        Returns:
            A filtered list containing only tasks for the specified pet.
        """
        return [t for t in tasks if t.pet_name == pet_name]

    # ------------------------------------------------------------------
    # Step 3: Recurring task completion
    # ------------------------------------------------------------------

    def mark_task_complete(self, task: Task) -> None:
        """Complete a task and, if recurring, add the next occurrence to the pet."""
        next_task = task.mark_complete()
        if next_task is not None:
            self.pet.add_task(next_task)

    # ------------------------------------------------------------------
    # Step 4: Conflict detection
    # ------------------------------------------------------------------

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        """Return warning strings for any two tasks whose time windows overlap.

        A conflict exists when a task's [start, start+duration) interval
        overlaps with another task's interval. Tasks without a start_time
        are skipped since they have no fixed window.
        """
        timed = [t for t in tasks if t.start_time]
        warnings: List[str] = []

        def to_minutes(hhmm: str) -> int:
            h, m = hhmm.split(":")
            return int(h) * 60 + int(m)

        for i, a in enumerate(timed):
            a_start = to_minutes(a.start_time)
            a_end = a_start + a.duration_minutes
            for b in timed[i + 1:]:
                b_start = to_minutes(b.start_time)
                b_end = b_start + b.duration_minutes
                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f"Conflict: '{a.title}' ({a.start_time}, {a.duration_minutes} min) "
                        f"overlaps '{b.title}' ({b.start_time}, {b.duration_minutes} min)"
                    )

        return warnings

    # ------------------------------------------------------------------
    # Output helpers
    # ------------------------------------------------------------------

    def explain_plan(self) -> str:
        """Return a human-readable summary of the scheduled tasks and time used."""
        if not self.scheduled_tasks:
            return "No tasks scheduled."
        lines = [f"Schedule for {self.pet.name} ({self.owner.name}):"]
        for task in self.scheduled_tasks:
            time_label = f" @ {task.start_time}" if task.start_time else ""
            lines.append(
                f"  - {task.title}{time_label} [{task.priority} priority, {task.duration_minutes} min]"
            )
        lines.append(
            f"Total time: {self.total_minutes_used}/{self.owner.available_minutes_per_day} min used."
        )
        return "\n".join(lines)

    def get_remaining_time(self) -> int:
        """Return how many minutes remain in the owner's daily budget."""
        return self.owner.available_minutes_per_day - self.total_minutes_used

    def _sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks from highest to lowest priority score."""
        return sorted(tasks, key=lambda t: t.get_priority_score(), reverse=True)

    def _fits_in_day(self, task: Task) -> bool:
        """Return True if adding this task stays within the daily time budget."""
        return self.total_minutes_used + task.duration_minutes <= self.owner.available_minutes_per_day


# ----------------------------------------------------------------------
# Quick terminal demo (python pawpal_system.py)
# ----------------------------------------------------------------------

if __name__ == "__main__":
    from datetime import date

    owner = Owner("Jordan", "", 120)
    pet = Pet("Mochi", "dog", 3)
    owner.add_pet(pet)
    scheduler = Scheduler(owner, pet)

    walk   = Task("Morning walk",  20, "high",   start_time="08:00", frequency="daily",  pet_name="Mochi", due_date=date.today())
    feed   = Task("Breakfast",     10, "high",   start_time="08:15", pet_name="Mochi")   # conflicts with walk
    meds   = Task("Medication",     5, "medium", start_time="09:00", frequency="weekly", pet_name="Mochi", due_date=date.today())
    groom  = Task("Grooming",      30, "low",    start_time="10:00", pet_name="Mochi")
    play   = Task("Playtime",      40, "medium", start_time="",      pet_name="Mochi")

    for t in [walk, feed, meds, groom, play]:
        scheduler.add_task(t)

    print("=== Sorted by time ===")
    for t in scheduler.sort_by_time(pet.assigned_tasks):
        print(f"  {t.start_time or '??:??'}  {t.title}")

    print("\n=== Conflict detection ===")
    conflicts = scheduler.detect_conflicts(pet.assigned_tasks)
    if conflicts:
        for w in conflicts:
            print(f"  WARNING: {w}")
    else:
        print("  No conflicts.")

    print("\n=== Generate schedule ===")
    scheduler.generate_schedule()
    print(scheduler.explain_plan())

    print("\n=== Mark 'Morning walk' complete (daily → creates tomorrow's) ===")
    scheduler.mark_task_complete(walk)
    pending = scheduler.filter_by_status(pet.assigned_tasks, completed=False)
    print(f"  Pending tasks after completion: {[t.title for t in pending]}")

    print("\n=== Filter by pet name ===")
    mochi_tasks = scheduler.filter_by_pet(pet.assigned_tasks, "Mochi")
    print(f"  Tasks for Mochi: {[t.title for t in mochi_tasks]}")
