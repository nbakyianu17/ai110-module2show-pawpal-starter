from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Literal


PRIORITY_ORDER = {"high": 3, "medium": 2, "low": 1}


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Literal["low", "medium", "high"]
    frequency: Literal["daily", "weekly", "once"] = "daily"
    completed: bool = False
    start_time: str | None = None  # HH:MM format, optional
    due_date: date | None = None

    def is_high_priority(self) -> bool:
        """Return True if this task has high priority."""
        return self.priority == "high"

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def reset(self) -> None:
        """Reset this task to incomplete so it can be scheduled again."""
        self.completed = False

    def generate_next_occurrence(self) -> "Task | None":
        """Return a new Task for the next recurrence, or None if the task does not repeat."""
        if self.frequency == "once":
            return None
        delta = timedelta(days=1) if self.frequency == "daily" else timedelta(weeks=1)
        next_due = (self.due_date or date.today()) + delta
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            start_time=self.start_time,
            due_date=next_due,
        )


@dataclass
class Pet:
    name: str
    species: Literal["dog", "cat", "other"]
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet's task list."""
        self.tasks.remove(task)

    def get_tasks(self) -> list[Task]:
        """Return all tasks assigned to this pet."""
        return self.tasks

    def get_pending_tasks(self) -> list[Task]:
        """Return only the tasks that have not yet been completed."""
        return [t for t in self.tasks if not t.completed]


class Owner:
    def __init__(self, name: str, available_minutes: int):
        self.name = name
        self.available_minutes = available_minutes
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's list."""
        self.pets.remove(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks())
        return tasks

    def get_all_pending_tasks(self) -> list[Task]:
        """Return all incomplete tasks across every pet."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.get_pending_tasks())
        return tasks


class DailyPlan:
    def __init__(
        self,
        scheduled_tasks: list[Task],
        skipped_tasks: list[Task],
        total_minutes_used: int,
        skipped_reasons: dict[str, str] | None = None,
    ):
        self.scheduled_tasks = scheduled_tasks
        self.skipped_tasks = skipped_tasks
        self.total_minutes_used = total_minutes_used
        self.skipped_reasons: dict[str, str] = skipped_reasons or {}

    def explain(self) -> str:
        """Return a human-readable summary of what was scheduled and why tasks were skipped."""
        lines = [f"=== Daily Plan ({self.total_minutes_used} min used) ===\n"]

        if self.scheduled_tasks:
            lines.append("Scheduled:")
            for task in self.scheduled_tasks:
                time_str = f" @ {task.start_time}" if task.start_time else ""
                lines.append(
                    f"  + {task.title}{time_str} ({task.duration_minutes} min, {task.priority} priority)"
                )
        else:
            lines.append("No tasks scheduled.")

        if self.skipped_tasks:
            lines.append("\nSkipped:")
            for task in self.skipped_tasks:
                reason = self.skipped_reasons.get(task.title, "unknown reason")
                lines.append(f"  - {task.title} — {reason}")

        return "\n".join(lines)


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def _sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks from highest to lowest priority."""
        return sorted(tasks, key=lambda t: PRIORITY_ORDER[t.priority], reverse=True)

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by start_time (HH:MM). Tasks without a start_time sort to the end."""
        return sorted(tasks, key=lambda t: t.start_time or "99:99")

    def filter_tasks(
        self,
        pet_name: str | None = None,
        completed: bool | None = None,
    ) -> list[Task]:
        """Return tasks filtered by pet name and/or completion status. None means no filter applied."""
        results = []
        pets = [p for p in self.owner.pets if pet_name is None or p.name == pet_name]
        for pet in pets:
            for task in pet.get_tasks():
                if completed is None or task.completed == completed:
                    results.append(task)
        return results

    def detect_conflicts(self) -> list[str]:
        """Return warning strings for any two tasks on the same pet that share a start_time."""
        warnings = []
        for pet in self.owner.pets:
            timed_tasks = [t for t in pet.get_tasks() if t.start_time]
            seen: dict[str, Task] = {}
            for task in timed_tasks:
                if task.start_time in seen:
                    other = seen[task.start_time]
                    warnings.append(
                        f"Conflict for {pet.name}: '{task.title}' and "
                        f"'{other.title}' both start at {task.start_time}"
                    )
                else:
                    seen[task.start_time] = task
        return warnings

    def mark_task_complete(self, task: Task, pet: Pet) -> Task | None:
        """Mark a task complete and add its next occurrence to the pet if it recurs."""
        task.mark_complete()
        next_task = task.generate_next_occurrence()
        if next_task:
            pet.add_task(next_task)
        return next_task

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks from the owner's pets without filtering."""
        return self.owner.get_all_tasks()

    def generate_plan(self) -> DailyPlan:
        """Build a daily plan by fitting pending tasks into the owner's available time, highest priority first."""
        pending = self.owner.get_all_pending_tasks()
        sorted_tasks = self._sort_by_priority(pending)

        scheduled: list[Task] = []
        skipped: list[Task] = []
        skipped_reasons: dict[str, str] = {}
        minutes_used = 0
        budget = self.owner.available_minutes

        for task in sorted_tasks:
            if minutes_used + task.duration_minutes <= budget:
                scheduled.append(task)
                minutes_used += task.duration_minutes
            else:
                remaining = budget - minutes_used
                skipped_reasons[task.title] = (
                    f"needs {task.duration_minutes} min, only {remaining} min left"
                )
                skipped.append(task)

        return DailyPlan(
            scheduled_tasks=scheduled,
            skipped_tasks=skipped,
            total_minutes_used=minutes_used,
            skipped_reasons=skipped_reasons,
        )
