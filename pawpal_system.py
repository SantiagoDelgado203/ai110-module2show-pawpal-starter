"""PawPal+ logic layer: Owner, Pet, Task, and Scheduler classes."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, timedelta

PRIORITY_RANKS = {"low": 1, "medium": 2, "high": 3}
VALID_FREQUENCIES = ("once", "daily", "weekly")
RECURRENCE_INTERVALS = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


def _time_to_minutes(time_str: str) -> int:
    """Convert an "HH:MM" string to minutes after midnight."""
    try:
        hours, minutes = time_str.strip().split(":")
        h, m = int(hours), int(minutes)
    except (AttributeError, ValueError):
        raise ValueError(f"Invalid time: {time_str!r} (expected HH:MM)") from None
    if not (0 <= h < 24 and 0 <= m < 60):
        raise ValueError(f"Invalid time: {time_str!r} (expected HH:MM)")
    return h * 60 + m


def _minutes_to_time(total: int) -> str:
    """Convert minutes after midnight to a zero-padded "HH:MM" string."""
    return f"{total // 60:02d}:{total % 60:02d}"


@dataclass
class Task:
    """A single pet care activity scheduled at a time on a given day."""

    description: str
    time: str  # "HH:MM", 24-hour clock
    duration_minutes: int = 15
    priority: str = "medium"  # "low" | "medium" | "high"
    frequency: str = "once"  # "once" | "daily" | "weekly"
    completed: bool = False
    due_date: date = field(default_factory=date.today)

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
        # Zero-pad ("7:30" -> "07:30") so plain string sorting is chronological.
        self.time = _minutes_to_time(_time_to_minutes(self.time))

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

    def end_minutes(self) -> int:
        """Return the task's end time as minutes after midnight."""
        return self.start_minutes() + self.duration_minutes

    def next_occurrence(self, completed_on: date | None = None) -> Task | None:
        """Return a fresh copy of this task for its next due date, or None if it doesn't recur.

        The next date is due_date + interval, rolled forward by whole intervals until it
        lands after the completion date. Completing a daily task on time gives tomorrow;
        completing a weekly Monday task late on Thursday gives next Monday (keeps the weekday).
        """
        interval = RECURRENCE_INTERVALS.get(self.frequency)
        if interval is None:
            return None
        completed_on = completed_on or date.today()
        next_due = self.due_date + interval
        while next_due <= completed_on:
            next_due += interval
        return replace(self, completed=False, due_date=next_due)


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

    def complete_task(self, task: Task, completed_on: date | None = None) -> Task | None:
        """Mark a task complete and, if it recurs, add and return its next occurrence."""
        if task.completed:
            return None  # already done: don't spawn a duplicate next occurrence
        task.mark_complete()
        next_task = task.next_occurrence(completed_on)
        if next_task is not None:
            self.add_task(next_task)
        return next_task

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


TaskPairs = list[tuple[Pet, Task]]


class Scheduler:
    """The 'brain' that gathers, orders, filters, and checks tasks across an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler that reads tasks from the given owner."""
        self.owner = owner

    def get_all_tasks(self) -> TaskPairs:
        """Retrieve all (pet, task) pairs from the owner's pets."""
        return self.owner.get_all_tasks()

    # --- Sorting ---------------------------------------------------------
    def sort_by_time(self, pairs: TaskPairs | None = None) -> TaskPairs:
        """Return tasks in chronological order (by due date, then "HH:MM" time).

        Times are zero-padded, so comparing the strings directly is chronological.
        """
        pairs = self.get_all_tasks() if pairs is None else pairs
        return sorted(pairs, key=lambda pair: (pair[1].due_date, pair[1].time))

    # --- Filtering -------------------------------------------------------
    def filter_tasks(
        self,
        pet_name: str | None = None,
        completed: bool | None = None,
        day: date | None = None,
        pairs: TaskPairs | None = None,
    ) -> TaskPairs:
        """Return tasks matching every filter given; a filter left as None is ignored."""
        pairs = self.get_all_tasks() if pairs is None else pairs
        return [
            (pet, task)
            for pet, task in pairs
            if (pet_name is None or pet.name.lower() == pet_name.lower())
            and (completed is None or task.completed == completed)
            and (day is None or task.due_date == day)
        ]

    def get_todays_schedule(self, day: date | None = None) -> TaskPairs:
        """Return the tasks due on the given day (default today) in time order."""
        return self.sort_by_time(self.filter_tasks(day=day or date.today()))

    # --- Recurring tasks -------------------------------------------------
    def mark_task_complete(
        self, pet_name: str, description: str, completed_on: date | None = None
    ) -> Task | None:
        """Complete the earliest pending task with this description for a pet.

        Returns the newly created next occurrence for daily/weekly tasks, else None.
        """
        pet = self.owner.get_pet(pet_name)
        if pet is None:
            raise ValueError(f"No pet named {pet_name!r}")
        matches = [t for t in pet.get_pending_tasks()
                   if t.description.lower() == description.lower()]
        if not matches:
            raise ValueError(f"{pet.name} has no pending task {description!r}")
        task = min(matches, key=lambda t: (t.due_date, t.time))
        return pet.complete_task(task, completed_on)

    # --- Conflict detection ----------------------------------------------
    def detect_conflicts(self, day: date | None = None) -> list[str]:
        """Return a warning string for each pair of tasks whose time windows overlap on a day.

        Lightweight sweep: sort by start time, keep the tasks still "running", and compare
        each new task only against those. Never raises; an empty list means no conflicts.
        """
        warnings: list[str] = []
        active: TaskPairs = []
        for pet, task in self.get_todays_schedule(day):
            active = [(p, t) for p, t in active if t.end_minutes() > task.start_minutes()]
            for other_pet, other in active:
                kind = "same time" if other.time == task.time else "overlap"
                warnings.append(
                    f"Conflict ({kind}): {other.time} {other_pet.name} - {other.description} "
                    f"({other.duration_minutes} min) and {task.time} {pet.name} - "
                    f"{task.description} ({task.duration_minutes} min)"
                )
            active.append((pet, task))
        return warnings

    # --- Output ----------------------------------------------------------
    def format_schedule(self, day: date | None = None) -> str:
        """Return the day's schedule as a readable multi-line string."""
        day = day or date.today()
        schedule = self.get_todays_schedule(day)
        lines = [f"Schedule for {self.owner.name} - {day:%A, %b %d}", "=" * 64]
        if not schedule:
            lines.append("  No tasks scheduled.")
            return "\n".join(lines)
        for pet, task in schedule:
            lines.append(self._format_row(pet, task))
        total = sum(task.duration_minutes for _, task in schedule)
        lines.append("-" * 64)
        noun = "task" if len(schedule) == 1 else "tasks"
        lines.append(f"  {len(schedule)} {noun}, {total} min total "
                     f"({self.owner.available_minutes} min available)")
        return "\n".join(lines)

    @staticmethod
    def _format_row(pet: Pet, task: Task) -> str:
        """Format one (pet, task) pair as a single aligned line."""
        status = "x" if task.completed else " "
        return (f"  [{status}] {task.time}  {pet.name:<8} {task.description:<18} "
                f"{task.duration_minutes:>3} min  ({task.priority}, {task.frequency})")
