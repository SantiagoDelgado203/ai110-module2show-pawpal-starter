"""PawPal+ logic layer: Owner, Pet, Task, and Scheduler classes."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    description: str
    time: str  # "HH:MM", 24-hour clock
    duration_minutes: int = 15
    priority: str = "medium"  # "low" | "medium" | "high"
    frequency: str = "once"  # "once" | "daily" | "weekly"
    completed: bool = False

    def mark_complete(self) -> None:
        pass

    def mark_incomplete(self) -> None:
        pass

    def priority_rank(self) -> int:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, description: str) -> bool:
        pass

    def get_pending_tasks(self) -> list[Task]:
        pass

    def task_count(self) -> int:
        pass


class Owner:
    def __init__(self, name: str, available_minutes: int = 120) -> None:
        self.name = name
        self.available_minutes = available_minutes
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, name: str) -> bool:
        pass

    def get_pet(self, name: str) -> Pet | None:
        pass

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        pass


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        pass

    def get_todays_schedule(self) -> list[tuple[Pet, Task]]:
        pass

    def format_schedule(self) -> str:
        pass
