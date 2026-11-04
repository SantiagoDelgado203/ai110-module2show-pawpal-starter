"""Quick tests for PawPal+ core behavior."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pawpal_system import Owner, Pet, Scheduler, Task  # noqa: E402


def test_mark_complete_changes_status():
    task = Task("Morning walk", "07:30")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert pet.task_count() == 0
    pet.add_task(Task("Breakfast", "08:00"))
    assert pet.task_count() == 1
    pet.add_task(Task("Evening walk", "18:00"))
    assert pet.task_count() == 2


def test_schedule_is_sorted_by_time_across_pets():
    owner = Owner("Jordan")
    dog, cat = Pet("Mochi", "dog"), Pet("Luna", "cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    dog.add_task(Task("Evening walk", "18:00"))
    cat.add_task(Task("Breakfast", "08:00"))
    dog.add_task(Task("Lunch", "12:00"))

    times = [task.time for _, task in Scheduler(owner).get_todays_schedule()]
    assert times == ["08:00", "12:00", "18:00"]
