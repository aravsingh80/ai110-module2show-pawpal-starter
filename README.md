# PawPal+ (Module 2 Project)

A smart pet care planning assistant built with Python and Streamlit.

## Features

- **Priority-based scheduling** — generates a daily plan by ranking tasks high → low and greedily fitting them into the owner's available time budget
- **Chronological sorting** — sorts any task list by `start_time` (HH:MM); tasks without a fixed time go last
- **Filtering** — view tasks by completion status (pending / completed) or by pet name
- **Recurring tasks** — daily tasks auto-generate a next occurrence (+1 day) when marked complete; weekly tasks shift by +7 days
- **Conflict detection** — flags any two timed tasks whose time windows overlap using interval arithmetic, displayed as inline warnings in the UI
- **Live metrics** — schedule view shows minutes used, minutes remaining, and a list of tasks that couldn't fit in the budget

## 📸 Demo

<a href="https://raw.githubusercontent.com/aravsingh80/ai110-module2show-pawpal-starter/main/course_images/pawpal_screenshot.png" target="_blank">
  <img src='https://raw.githubusercontent.com/aravsingh80/ai110-module2show-pawpal-starter/main/course_images/pawpal_screenshot.png' title='PawPal App' width='' alt='PawPal App' class='center-block' />
</a>

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Smarter Scheduling

Beyond basic task entry, PawPal+ includes four algorithmic features in `pawpal_system.py`:

**Sort by time** — `Scheduler.sort_by_time(tasks)` orders any task list by `start_time` ("HH:MM") ascending. Tasks without a fixed start time are placed at the end. Useful for displaying a chronological view of the day.

**Filter by status / pet** — `filter_by_status(tasks, completed)` returns only pending or completed tasks. `filter_by_pet(tasks, pet_name)` narrows the list to a single pet. Both can be chained for views like "all incomplete tasks for Mochi".

**Recurring tasks** — `Task` now accepts a `frequency` field (`"daily"` or `"weekly"`). Calling `Scheduler.mark_task_complete(task)` sets the task as done and automatically creates the next occurrence (shifted by 1 day or 7 days via `timedelta`) and adds it back to the pet's task list.

**Conflict detection** — `Scheduler.detect_conflicts(tasks)` compares every pair of timed tasks using the interval-overlap test (`A.start < B.end and B.start < A.end`). It returns a list of plain-English warning strings rather than raising an error, so the UI can surface the warning without crashing.

> **Tradeoff:** `generate_schedule` ranks tasks by priority and ignores `start_time` when deciding what fits in the day. Conflict detection is intentionally separate — the scheduler tells you *what* to do, and `detect_conflicts` tells you *if* anything clashes.

## Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest tests/test_pawpal.py -v
```

**What the tests cover (27 tests):**

| Area | Tests |
|---|---|
| Task completion | `mark_complete` sets flag; one-off returns `None` |
| Recurring — daily | Next occurrence is +1 day; attributes are preserved; works without `due_date` |
| Recurring — weekly | Next occurrence is +7 days |
| Priority scoring | `high=3`, `medium=2`, `low=1`, unknown=0 |
| Pet management | `add_task` appends; `get_tasks_by_priority` sorts correctly; empty pet returns `[]` |
| `sort_by_time` | Chronological HH:MM order; untimed tasks go last; empty list |
| `filter_by_status` | Returns only pending or only completed tasks |
| `filter_by_pet` | Matches by name; returns `[]` for no match |
| Conflict detection | No conflict; partial overlap; exact same start time; skips untimed tasks |
| `generate_schedule` | Respects time budget; high priority first; empty pet; all tasks over budget |
| `mark_task_complete` | Recurring adds next occurrence to pet; one-off does not |

**Confidence level: ★★★★☆**

Core scheduling logic, recurrence, sorting, filtering, and conflict detection are all verified. The remaining gap is integration-level testing (Streamlit UI interactions and multi-pet scenarios with shared time budgets).

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
