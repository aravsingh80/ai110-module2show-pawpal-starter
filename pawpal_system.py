from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    category: str = ""
    time_of_day: str = ""  # "morning", "afternoon", "evening", or ""
    is_completed: bool = False

    def get_priority_score(self) -> int:
        return {"low": 1, "medium": 2, "high": 3}.get(self.priority, 0)

    def mark_complete(self) -> None:
        self.is_completed = True


@dataclass
class Pet:
    name: str
    species: str
    age: int
    preferences: List[str] = field(default_factory=list)
    assigned_tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.assigned_tasks.append(task)

    def get_tasks_by_priority(self) -> List[Task]:
        return sorted(self.assigned_tasks, key=lambda t: t.get_priority_score(), reverse=True)


class Owner:
    def __init__(self, name: str, email: str, available_minutes_per_day: int):
        self.name = name
        self.email = email
        self.available_minutes_per_day = available_minutes_per_day
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def get_total_available_time(self) -> int:
        return self.available_minutes_per_day


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.scheduled_tasks: List[Task] = []
        self.total_minutes_used: int = 0

    def add_task(self, task: Task) -> None:
        self.pet.add_task(task)

    def generate_schedule(self) -> List[Task]:
        self.scheduled_tasks = []
        self.total_minutes_used = 0
        for task in self._sort_by_priority(self.pet.assigned_tasks):
            if self._fits_in_day(task):
                self.scheduled_tasks.append(task)
                self.total_minutes_used += task.duration_minutes
        return self.scheduled_tasks

    def explain_plan(self) -> str:
        if not self.scheduled_tasks:
            return "No tasks scheduled."
        lines = [f"Schedule for {self.pet.name} ({self.owner.name}):"]
        for task in self.scheduled_tasks:
            lines.append(
                f"  - {task.title} [{task.priority} priority, {task.duration_minutes} min]"
            )
        lines.append(
            f"Total time: {self.total_minutes_used}/{self.owner.available_minutes_per_day} min used."
        )
        return "\n".join(lines)

    def get_remaining_time(self) -> int:
        return self.owner.available_minutes_per_day - self.total_minutes_used

    def _sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        return sorted(tasks, key=lambda t: t.get_priority_score(), reverse=True)

    def _fits_in_day(self, task: Task) -> bool:
        return self.total_minutes_used + task.duration_minutes <= self.owner.available_minutes_per_day
