"""PawPal+ logic layer: Owner, Pet, Task, and Scheduler classes."""

from __future__ import annotations

from dataclasses import dataclass, field

PRIORITY_RANKS = {"low": 1, "medium": 2, "high": 3}
VALID_FREQUENCIES = ("once", "daily", "weekly")


def _time_to_minutes(time_str: str) -> int:
    """Convert an "HH:MM" string to minutes after midnight."""
    hours, minutes = time_str.strip().split(":")
    h, m = int(hours), int(minutes)
    if not (0 <= h < 24 and 0 <= m < 60):
        raise ValueError(f"Invalid time: {time_str!r}")
    return h * 60 + m


@dataclass
class Task:
    """A single pet care activity scheduled at a time of day."""

    description: str
    time: str  # "HH:MM", 24-hour clock
    duration_minutes: int = 15
    priority: str = "medium"  # "low" | "medium" | "high"
    frequency: str = "once"  # "once" | "daily" | "weekly"
    completed: bool = False

    def __post_init__(self) -> None:
        """Normalize and validate fields after construction."""
        self.priority = self.priority.lower()
        self.frequency = self.frequency.lower()
        if self.priority not in PRIORITY_RANKS:
            raise ValueError(f"Priority must be one of {list(PRIORITY_RANKS)}")
        if self.frequency not in VALID_FREQUENCIES:
            raise ValueError(f"Frequency must be one of {list(VALID_FREQUENCIES)}")
        if self.duration_minutes <= 0:
            raise ValueError("Duration must be a positive number of minutes")
        _time_to_minutes(self.time)  # raises ValueError if malformed

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as not done."""
        self.completed = False

    def priority_rank(self) -> int:
        """Return a numeric rank for the priority (higher = more important)."""
        return PRIORITY_RANKS[self.priority]

    def start_minutes(self) -> int:
        """Return the task's start time as minutes after midnight."""
        return _time_to_minutes(self.time)


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        self.tasks.append(task)

    def remove_task(self, description: str) -> bool:
        """Remove the first task matching the description; return True if removed."""
        for i, task in enumerate(self.tasks):
            if task.description.lower() == description.lower():
                del self.tasks[i]
                return True
        return False

    def get_pending_tasks(self) -> list[Task]:
        """Return the tasks that have not been completed yet."""
        return [t for t in self.tasks if not t.completed]

    def task_count(self) -> int:
        """Return how many tasks this pet has."""
        return len(self.tasks)


class Owner:
    """A pet owner who manages one or more pets."""

    def __init__(self, name: str, available_minutes: int = 120) -> None:
        """Create an owner with a name and daily minutes available for pet care."""
        self.name = name
        self.available_minutes = available_minutes
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet; pet names must be unique per owner."""
        if self.get_pet(pet.name) is not None:
            raise ValueError(f"{self.name} already has a pet named {pet.name!r}")
        self.pets.append(pet)

    def remove_pet(self, name: str) -> bool:
        """Remove a pet by name; return True if a pet was removed."""
        pet = self.get_pet(name)
        if pet is None:
            return False
        self.pets.remove(pet)
        return True

    def get_pet(self, name: str) -> Pet | None:
        """Look up a pet by name (case-insensitive)."""
        for pet in self.pets:
            if pet.name.lower() == name.lower():
                return pet
        return None

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (pet, task) pair across all of this owner's pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


class Scheduler:
    """The 'brain' that gathers and organizes tasks across an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler that reads tasks from the given owner."""
        self.owner = owner

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Retrieve all (pet, task) pairs from the owner's pets."""
        return self.owner.get_all_tasks()

    def get_todays_schedule(self) -> list[tuple[Pet, Task]]:
        """Return today's tasks ordered by time, breaking ties by higher priority."""
        return sorted(
            self.get_all_tasks(),
            key=lambda pair: (pair[1].start_minutes(), -pair[1].priority_rank()),
        )

    def format_schedule(self) -> str:
        """Return today's schedule as a readable multi-line string."""
        schedule = self.get_todays_schedule()
        lines = [f"Today's Schedule for {self.owner.name}", "=" * 64]
        if not schedule:
            lines.append("  No tasks scheduled.")
            return "\n".join(lines)
        for pet, task in schedule:
            status = "x" if task.completed else " "
            lines.append(
                f"  [{status}] {task.time}  {pet.name:<8} {task.description:<18} "
                f"{task.duration_minutes:>3} min  ({task.priority}, {task.frequency})"
            )
        total = sum(task.duration_minutes for _, task in schedule)
        lines.append("-" * 64)
        lines.append(f"  {len(schedule)} tasks, {total} min total "
                     f"({self.owner.available_minutes} min available)")
        return "\n".join(lines)
