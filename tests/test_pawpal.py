"""Automated tests for the PawPal+ logic layer."""

import os
import sys
from datetime import date, timedelta

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pawpal_system import Owner, Pet, Scheduler, Task  # noqa: E402

MONDAY = date(2026, 11, 2)  # fixed date so tests don't depend on when they run


@pytest.fixture
def household():
    """Owner with a dog and a cat, no tasks yet."""
    owner = Owner("Jordan", available_minutes=60)
    dog, cat = Pet("Mochi", "dog", 3), Pet("Luna", "cat", 5)
    owner.add_pet(dog)
    owner.add_pet(cat)
    return owner, dog, cat, Scheduler(owner)


# --- Task basics ----------------------------------------------------------

def test_mark_complete_changes_status():
    task = Task("Morning walk", "07:30")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True
    task.mark_incomplete()
    assert task.completed is False


def test_adding_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert pet.task_count() == 0
    pet.add_task(Task("Breakfast", "08:00"))
    assert pet.task_count() == 1
    pet.add_task(Task("Evening walk", "18:00"))
    assert pet.task_count() == 2


def test_time_is_zero_padded():
    assert Task("Breakfast", "8:05").time == "08:05"


@pytest.mark.parametrize("kwargs", [
    {"time": "25:00"},
    {"time": "noon"},
    {"priority": "urgent"},
    {"frequency": "monthly"},
    {"duration_minutes": 0},
])
def test_invalid_task_fields_raise(kwargs):
    fields = {"description": "Walk", "time": "08:00", **kwargs}
    with pytest.raises(ValueError):
        Task(**fields)


def test_duplicate_pet_name_rejected(household):
    owner, *_ = household
    with pytest.raises(ValueError):
        owner.add_pet(Pet("mochi", "dog"))  # case-insensitive duplicate


# --- Sorting --------------------------------------------------------------

def test_sort_by_time_is_chronological_across_pets(household):
    _, dog, cat, scheduler = household
    dog.add_task(Task("Evening walk", "18:00", due_date=MONDAY))
    cat.add_task(Task("Breakfast", "8:00", due_date=MONDAY))
    dog.add_task(Task("Lunch", "12:00", due_date=MONDAY))
    cat.add_task(Task("Late snack", "09:30", due_date=MONDAY))

    times = [t.time for _, t in scheduler.sort_by_time()]
    assert times == ["08:00", "09:30", "12:00", "18:00"]


def test_sort_by_time_orders_by_date_first(household):
    _, dog, _, scheduler = household
    dog.add_task(Task("Tomorrow early", "06:00", due_date=MONDAY + timedelta(days=1)))
    dog.add_task(Task("Today late", "20:00", due_date=MONDAY))
    assert [t.description for _, t in scheduler.sort_by_time()] == ["Today late", "Tomorrow early"]


def test_sort_by_priority_then_time(household):
    _, dog, cat, scheduler = household
    dog.add_task(Task("Play", "07:00", priority="low", due_date=MONDAY))
    cat.add_task(Task("Meds B", "12:00", priority="high", due_date=MONDAY))
    dog.add_task(Task("Meds A", "09:00", priority="high", due_date=MONDAY))
    cat.add_task(Task("Brush", "08:00", priority="medium", due_date=MONDAY))

    order = [t.description for _, t in scheduler.sort_by_priority()]
    assert order == ["Meds A", "Meds B", "Brush", "Play"]


def test_empty_schedule_is_empty_list(household):
    *_, scheduler = household
    assert scheduler.get_todays_schedule(MONDAY) == []
    assert scheduler.detect_conflicts(MONDAY) == []
    assert "No tasks scheduled" in scheduler.format_schedule(MONDAY)


# --- Filtering ------------------------------------------------------------

def test_filter_by_pet_and_status(household):
    _, dog, cat, scheduler = household
    walk = Task("Walk", "07:00", due_date=MONDAY)
    dog.add_task(walk)
    dog.add_task(Task("Dinner", "18:00", due_date=MONDAY))
    cat.add_task(Task("Breakfast", "08:00", due_date=MONDAY))
    walk.mark_complete()

    assert {t.description for _, t in scheduler.filter_tasks(pet_name="MOCHI")} == {"Walk", "Dinner"}
    assert [t.description for _, t in scheduler.filter_tasks(completed=True)] == ["Walk"]
    pending_dog = scheduler.filter_tasks(pet_name="Mochi", completed=False)
    assert [t.description for _, t in pending_dog] == ["Dinner"]
    assert scheduler.filter_tasks(pet_name="Nobody") == []


def test_todays_schedule_only_includes_that_day(household):
    _, dog, _, scheduler = household
    dog.add_task(Task("Today", "08:00", due_date=MONDAY))
    dog.add_task(Task("Tomorrow", "08:00", due_date=MONDAY + timedelta(days=1)))
    assert [t.description for _, t in scheduler.get_todays_schedule(MONDAY)] == ["Today"]


# --- Recurrence -----------------------------------------------------------

def test_completing_daily_task_creates_next_day_task(household):
    _, dog, _, scheduler = household
    dog.add_task(Task("Morning walk", "07:30", frequency="daily", due_date=MONDAY))

    nxt = scheduler.mark_task_complete("Mochi", "Morning walk", completed_on=MONDAY)

    assert nxt is not None
    assert nxt.due_date == MONDAY + timedelta(days=1)
    assert nxt.completed is False
    assert (nxt.time, nxt.description, nxt.frequency) == ("07:30", "Morning walk", "daily")
    assert dog.task_count() == 2
    assert dog.tasks[0].completed is True  # original kept as history


def test_completing_weekly_task_creates_task_one_week_later(household):
    _, _, cat, scheduler = household
    cat.add_task(Task("Flea meds", "12:00", frequency="weekly", due_date=MONDAY))
    nxt = scheduler.mark_task_complete("Luna", "Flea meds", completed_on=MONDAY)
    assert nxt.due_date == MONDAY + timedelta(weeks=1)


def test_late_weekly_completion_keeps_weekday(household):
    _, _, cat, scheduler = household
    cat.add_task(Task("Flea meds", "12:00", frequency="weekly", due_date=MONDAY))
    thursday = MONDAY + timedelta(days=3)
    nxt = scheduler.mark_task_complete("Luna", "Flea meds", completed_on=thursday)
    assert nxt.due_date == MONDAY + timedelta(weeks=1)
    assert nxt.due_date.weekday() == MONDAY.weekday()


def test_once_task_does_not_recur(household):
    _, dog, _, scheduler = household
    dog.add_task(Task("Vet", "14:00", frequency="once", due_date=MONDAY))
    assert scheduler.mark_task_complete("Mochi", "Vet", completed_on=MONDAY) is None
    assert dog.task_count() == 1


def test_completing_twice_does_not_duplicate(household):
    _, dog, _, _ = household
    task = Task("Walk", "07:00", frequency="daily", due_date=MONDAY)
    dog.add_task(task)
    assert dog.complete_task(task, MONDAY) is not None
    assert dog.complete_task(task, MONDAY) is None
    assert dog.task_count() == 2


def test_mark_task_complete_unknown_pet_or_task_raises(household):
    *_, scheduler = household
    with pytest.raises(ValueError):
        scheduler.mark_task_complete("Ghost", "Walk")
    with pytest.raises(ValueError):
        scheduler.mark_task_complete("Mochi", "Walk")


# --- Conflict detection ---------------------------------------------------

def test_detects_tasks_at_same_time_across_pets(household):
    _, dog, cat, scheduler = household
    dog.add_task(Task("Walk", "08:00", 30, due_date=MONDAY))
    cat.add_task(Task("Breakfast", "08:00", 10, due_date=MONDAY))

    warnings = scheduler.detect_conflicts(MONDAY)
    assert len(warnings) == 1
    assert "same time" in warnings[0]
    assert "Walk" in warnings[0] and "Breakfast" in warnings[0]


def test_detects_overlapping_windows(household):
    _, dog, _, scheduler = household
    dog.add_task(Task("Vet", "14:00", 60, due_date=MONDAY))
    dog.add_task(Task("Walk", "14:30", 20, due_date=MONDAY))
    warnings = scheduler.detect_conflicts(MONDAY)
    assert len(warnings) == 1 and "overlap" in warnings[0]


def test_back_to_back_tasks_are_not_conflicts(household):
    _, dog, _, scheduler = household
    dog.add_task(Task("Walk", "08:00", 30, due_date=MONDAY))
    dog.add_task(Task("Breakfast", "08:30", 10, due_date=MONDAY))
    assert scheduler.detect_conflicts(MONDAY) == []


def test_conflicts_on_other_days_are_ignored(household):
    _, dog, cat, scheduler = household
    dog.add_task(Task("Walk", "08:00", due_date=MONDAY))
    cat.add_task(Task("Breakfast", "08:00", due_date=MONDAY + timedelta(days=1)))
    assert scheduler.detect_conflicts(MONDAY) == []


# --- Next available slot & daily plan ------------------------------------

def test_next_available_slot_finds_first_gap(household):
    _, dog, cat, scheduler = household
    dog.add_task(Task("Walk", "07:00", 30, due_date=MONDAY))
    cat.add_task(Task("Breakfast", "07:30", 15, due_date=MONDAY))
    dog.add_task(Task("Training", "09:00", 30, due_date=MONDAY))

    assert scheduler.find_next_available_slot(30, MONDAY) == "07:45"
    assert scheduler.find_next_available_slot(90, MONDAY) == "09:30"


def test_next_available_slot_none_when_day_full(household):
    _, dog, _, scheduler = household
    dog.add_task(Task("All-day daycare", "07:00", 900, due_date=MONDAY))
    assert scheduler.find_next_available_slot(15, MONDAY) is None


def test_build_plan_keeps_high_priority_within_budget(household):
    owner, dog, cat, scheduler = household  # 60 minutes available
    dog.add_task(Task("Long hike", "07:00", 50, "low", due_date=MONDAY))
    cat.add_task(Task("Insulin", "09:00", 10, "high", due_date=MONDAY))
    dog.add_task(Task("Walk", "12:00", 40, "medium", due_date=MONDAY))

    plan = {e.task.description: e for e in scheduler.build_plan(MONDAY)}
    assert plan["Insulin"].included and plan["Walk"].included
    assert not plan["Long hike"].included
    assert "skipped" in plan["Long hike"].reason
    assert sum(e.task.duration_minutes for e in plan.values() if e.included) <= owner.available_minutes


# --- Persistence ----------------------------------------------------------

def test_save_and_load_json_round_trip(household, tmp_path):
    owner, dog, cat, _ = household
    dog.add_task(Task("Walk", "07:00", 30, "high", "daily", due_date=MONDAY))
    done = Task("Brush", "19:00", 10, "low", "weekly", due_date=MONDAY)
    done.mark_complete()
    cat.add_task(done)

    path = tmp_path / "data.json"
    owner.save_to_json(path)
    restored = Owner.load_from_json(path)

    assert restored.to_dict() == owner.to_dict()
    assert restored.get_pet("Luna").tasks[0].completed is True
    assert restored.get_pet("Mochi").tasks[0].due_date == MONDAY


def test_load_missing_file_returns_none(tmp_path):
    assert Owner.load_from_json(tmp_path / "nope.json") is None


# --- Formatting -----------------------------------------------------------

def test_task_emoji_matches_keywords():
    assert Task("Morning walk", "07:00").emoji() == "🦮"
    assert Task("Give pill", "07:00").emoji() == "💊"
    assert Task("Something else", "07:00").emoji() == "🐾"
