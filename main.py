"""CLI demo for PawPal+: exercises sorting, filtering, recurrence, and conflict detection."""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def section(title: str) -> None:
    """Print a section header."""
    print(f"\n### {title}")


def main() -> None:
    """Build sample data and demonstrate the scheduler's features."""
    today = date.today()
    owner = Owner("Jordan", available_minutes=120)

    mochi = Pet("Mochi", species="dog", age=3)
    luna = Pet("Luna", species="cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Added out of order on purpose so sorting is visible.
    mochi.add_task(Task("Evening walk", "18:30", 30, "medium", "daily"))
    mochi.add_task(Task("Morning walk", "07:30", 30, "high", "daily"))
    luna.add_task(Task("Flea medication", "12:00", 5, "high", "weekly"))
    luna.add_task(Task("Breakfast", "8:00", 10, "high", "daily"))
    mochi.add_task(Task("Vet appointment", "14:00", 60, "medium", "once"))
    luna.add_task(Task("Brush fur", "14:00", 15, "low", "weekly"))  # same time as vet

    scheduler = Scheduler(owner)

    section("Today's schedule (sorted by time)")
    print(scheduler.format_schedule())

    section("Filter: only Luna's tasks")
    for pet, task in scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Luna")):
        print(Scheduler._format_row(pet, task))

    section("Conflict check")
    conflicts = scheduler.detect_conflicts()
    for warning in conflicts:
        print(f"  WARNING: {warning}")
    if not conflicts:
        print("  No conflicts.")

    section("Recurring tasks: completing Morning walk and Flea medication")
    for pet_name, desc in [("Mochi", "Morning walk"), ("Luna", "Flea medication")]:
        nxt = scheduler.mark_task_complete(pet_name, desc)
        print(f"  {desc} done -> next occurrence on {nxt.due_date:%a %b %d} at {nxt.time}")
    once = scheduler.mark_task_complete("Mochi", "Vet appointment")
    print(f"  Vet appointment done -> next occurrence: {once}")

    section("Filter: tasks still pending today")
    for pet, task in scheduler.sort_by_time(scheduler.filter_tasks(completed=False, day=today)):
        print(Scheduler._format_row(pet, task))

    section("Tomorrow's schedule")
    print(scheduler.format_schedule(today + timedelta(days=1)))


if __name__ == "__main__":
    main()
