from dataclasses import dataclass, field
from typing import Literal


@dataclass
class Pet:
    name: str
    species: Literal["dog", "cat", "other"]


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Literal["low", "medium", "high"]

    def is_high_priority(self) -> bool:
        pass


class Owner:
    def __init__(self, name: str, available_minutes: int, pet: Pet):
        self.name = name
        self.available_minutes = available_minutes
        self.pet = pet
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def get_tasks(self) -> list[Task]:
        pass


class DailyPlan:
    def __init__(
        self,
        scheduled_tasks: list[Task],
        skipped_tasks: list[Task],
        total_minutes_used: int,
    ):
        self.scheduled_tasks = scheduled_tasks
        self.skipped_tasks = skipped_tasks
        self.total_minutes_used = total_minutes_used

    def explain(self) -> str:
        pass


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def generate_plan(self) -> DailyPlan:
        pass
