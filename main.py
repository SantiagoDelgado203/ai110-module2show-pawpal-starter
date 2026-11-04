"""CLI demo for PawPal+: builds an owner with pets and tasks, then prints today's schedule."""

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    """Build sample data and print today's schedule."""
    owner = Owner("Jordan", available_minutes=120)

    mochi = Pet("Mochi", species="dog", age=3)
    luna = Pet("Luna", species="cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Added out of order on purpose so the scheduler's sorting is visible.
    mochi.add_task(Task("Evening walk", "18:30", 30, "medium", "daily"))
    mochi.add_task(Task("Morning walk", "07:30", 30, "high", "daily"))
    luna.add_task(Task("Breakfast", "08:00", 10, "high", "daily"))
    luna.add_task(Task("Flea medication", "12:00", 5, "high", "weekly"))
    mochi.add_task(Task("Vet appointment", "14:00", 60, "medium", "once"))

    luna.tasks[0].mark_complete()  # Breakfast is already done

    scheduler = Scheduler(owner)
    print(scheduler.format_schedule())


if __name__ == "__main__":
    main()
