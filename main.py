"""CLI demo for PawPal+: exercises sorting, filtering, recurrence, conflicts, planning, and persistence."""

import os
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

from pawpal_system import Owner, Pet, Scheduler, Task

# Emojis need UTF-8 even when output is redirected to a file on Windows.
sys.stdout.reconfigure(encoding="utf-8")
# ANSI colors only in a real terminal (and never when NO_COLOR is set).
USE_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ


def section(title: str) -> None:
    """Print a section header."""
    print(f"\n### {title}")


def print_rows(pairs) -> None:
    """Print (pet, task) pairs one per line."""
    for pet, task in pairs:
        print(Scheduler.format_row(pet, task, USE_COLOR))


def build_demo_owner() -> Owner:
    """Create an owner with two pets and a set of tasks added out of order."""
    owner = Owner("Jordan", available_minutes=120)
    mochi = Pet("Mochi", species="dog", age=3)
    luna = Pet("Luna", species="cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task("Evening walk", "18:30", 30, "medium", "daily"))
    mochi.add_task(Task("Morning walk", "07:30", 30, "high", "daily"))
    luna.add_task(Task("Flea medication", "12:00", 5, "high", "weekly"))
    luna.add_task(Task("Breakfast", "8:00", 10, "high", "daily"))
    mochi.add_task(Task("Vet appointment", "14:00", 60, "medium", "once"))
    luna.add_task(Task("Brush fur", "14:00", 15, "low", "weekly"))  # same time as vet
    mochi.add_task(Task("Fetch in the yard", "16:00", 20, "low", "daily"))
    return owner


def main() -> None:
    """Demonstrate each scheduler feature in the terminal."""
    today = date.today()
    owner = build_demo_owner()
    scheduler = Scheduler(owner)

    section("Today's schedule (sorted by time)")
    print(scheduler.format_schedule(color=USE_COLOR))

    section("Sorted by priority, then time")
    print_rows(scheduler.sort_by_priority(scheduler.filter_tasks(day=today)))

    section("Filter: only Luna's tasks")
    print_rows(scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Luna")))

    section("Conflict check")
    conflicts = scheduler.detect_conflicts()
    for warning in conflicts:
        print(f"  ⚠️  {warning}")
    if not conflicts:
        print("  No conflicts.")

    section(f"Daily plan within {owner.available_minutes} available minutes")
    for entry in scheduler.build_plan():
        mark = "✔" if entry.included else "✘"
        print(f"  {mark} {entry.task.time} {entry.pet.name:<6} "
              f"{entry.task.description:<17} {entry.reason}")

    section("Next available slot")
    for minutes in (30, 90):
        slot = scheduler.find_next_available_slot(minutes)
        print(f"  {minutes:>3}-minute task fits at: {slot}")

    section("Recurring tasks: completing Morning walk and Flea medication")
    for pet_name, desc in [("Mochi", "Morning walk"), ("Luna", "Flea medication")]:
        nxt = scheduler.mark_task_complete(pet_name, desc)
        print(f"  {desc} done -> next occurrence {nxt.due_date:%a %b %d} at {nxt.time}")
    once = scheduler.mark_task_complete("Mochi", "Vet appointment")
    print(f"  Vet appointment done -> next occurrence: {once}")

    section("Filter: tasks still pending today")
    print_rows(scheduler.sort_by_time(scheduler.filter_tasks(completed=False, day=today)))

    section("Tomorrow's schedule")
    print(scheduler.format_schedule(today + timedelta(days=1), color=USE_COLOR))

    section("Persistence: save to JSON and load it back")
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "data.json"
        owner.save_to_json(path)
        restored = Owner.load_from_json(path)
    print(f"  Saved and reloaded {len(restored.pets)} pets with "
          f"{len(restored.get_all_tasks())} tasks; matches original: "
          f"{restored.to_dict() == owner.to_dict()}")


if __name__ == "__main__":
    main()
