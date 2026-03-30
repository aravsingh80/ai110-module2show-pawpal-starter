# PawPal+ — Final UML Class Diagram

Paste the Mermaid code below into [mermaid.live](https://mermaid.live) to render it,
or use any Markdown viewer that supports Mermaid fenced code blocks.

```mermaid
classDiagram
    class Task {
        +String title
        +int duration_minutes
        +String priority
        +String category
        +String time_of_day
        +String start_time
        +String frequency
        +String pet_name
        +date due_date
        +bool is_completed
        +get_priority_score() int
        +mark_complete() Task
    }

    class Pet {
        +String name
        +String species
        +int age
        +List~String~ preferences
        +List~Task~ assigned_tasks
        +add_task(task: Task) void
        +get_tasks_by_priority() List~Task~
    }

    class Owner {
        +String name
        +String email
        +int available_minutes_per_day
        +List~Pet~ pets
        +add_pet(pet: Pet) void
        +get_total_available_time() int
    }

    class Scheduler {
        +Owner owner
        +Pet pet
        +List~Task~ scheduled_tasks
        +int total_minutes_used
        +add_task(task: Task) void
        +generate_schedule() List~Task~
        +explain_plan() String
        +get_remaining_time() int
        +sort_by_time(tasks: List~Task~) List~Task~
        +filter_by_status(tasks, completed: bool) List~Task~
        +filter_by_pet(tasks, pet_name: str) List~Task~
        +mark_task_complete(task: Task) void
        +detect_conflicts(tasks: List~Task~) List~String~
        -_sort_by_priority(tasks: List~Task~) List~Task~
        -_fits_in_day(task: Task) bool
    }

    Owner "1" --> "1..*" Pet : owns
    Pet "1" --> "0..*" Task : has
    Scheduler "1" --> "1" Owner : plans for
    Scheduler "1" --> "1" Pet : schedules tasks for
    Scheduler "1" --> "0..*" Task : manages
    Task ..> Task : mark_complete() returns next occurrence
```

## Changes from initial UML

| What changed | Why |
|---|---|
| `Task` gained `start_time`, `frequency`, `pet_name`, `due_date` | Needed for time-based sorting, recurring logic, per-pet filtering, and next-occurrence date math |
| `Task.mark_complete()` now returns `Task` (next occurrence) | Recurring support — returns `None` for one-off tasks |
| `Scheduler` gained `sort_by_time`, `filter_by_status`, `filter_by_pet`, `mark_task_complete`, `detect_conflicts` | Phase 3 algorithmic layer — sorting, filtering, recurrence, and conflict detection |
| Self-referential `Task ..> Task` dependency added | `mark_complete()` creates and returns a new `Task` instance |
