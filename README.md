# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Output of `python main.py` (CLI demo):

```
Today's Schedule for Jordan
================================================================
  [ ] 07:30  Mochi    Morning walk        30 min  (high, daily)
  [x] 08:00  Luna     Breakfast           10 min  (high, daily)
  [ ] 12:00  Luna     Flea medication      5 min  (high, weekly)
  [ ] 14:00  Mochi    Vet appointment     60 min  (medium, once)
  [ ] 18:30  Mochi    Evening walk        30 min  (medium, daily)
----------------------------------------------------------------
  5 tasks, 135 min total (120 min available)
```

## 🧪 Testing PawPal+

Run the suite from the project root:

```bash
python -m pytest
```

`tests/test_pawpal.py` has 31 tests. They use a fixed date (Monday 2026-11-02), so results don't depend on what day you run them.

| Area | What is verified |
|------|------------------|
| **Task basics** | `mark_complete()` / `mark_incomplete()` change the status; adding a task increases a pet's count; `"8:05"` is stored as `"08:05"`; invalid time, priority, frequency, or duration raises `ValueError`; duplicate pet names are rejected. |
| **Sorting** | `sort_by_time()` returns chronological order across pets and orders by date before time; `sort_by_priority()` puts high before low and uses time to break ties. |
| **Filtering** | Filtering by pet (case-insensitive), by completion status, by day, and combinations; an unknown pet returns `[]`. |
| **Recurrence** | Completing a daily task creates one due the next day with the same details; weekly tasks come back +7 days; a weekly task finished late still lands on its original weekday; `once` tasks don't recur; completing twice doesn't create a duplicate; unknown pet/task raises. |
| **Conflict detection** | Same start time across pets is flagged; overlapping windows (14:00 60 min vs 14:30) are flagged; back-to-back tasks are *not* flagged; tasks on other days are ignored. |
| **Edge cases** | A household with no tasks gives an empty schedule, no conflicts, and a "No tasks scheduled" message. |
| **Next slot & daily plan** | Finds the first gap of a given length, returns `None` when the day is full; `build_plan()` keeps high-priority tasks inside the owner's time budget and explains what was skipped. |
| **Persistence** | `save_to_json()` → `load_from_json()` round-trips pets, tasks, completion status, and dates exactly; a missing file returns `None`. |

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.13.1, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\santi\OneDrive\Desktop\College\Fall_2026\Software Engineering\PawPal
plugins: anyio-4.12.1, typeguard-4.5.1
collected 31 items

tests\test_pawpal.py ...............................                     [100%]

============================= 31 passed in 0.12s ==============================
```

**Confidence level: ⭐⭐⭐⭐☆ (4/5).** Every core behavior (sorting, filtering, recurrence, conflicts) has happy-path and edge-case tests, and all of them pass. I'm holding back one star because the Streamlit UI is only checked by hand, and some situations aren't covered yet: tasks that run past midnight, time zones, and editing a recurring task after its next copy already exists.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | `sorted()` with a `lambda` key of `(due_date, time)`. Times are zero-padded on creation (`"7:30"` becomes `"07:30"`), so comparing the `"HH:MM"` strings gives chronological order. |
| Filtering | `Scheduler.filter_tasks(pet_name=, completed=, day=)` | Each filter is optional, and filters combine (e.g. pending tasks for Luna today). `get_todays_schedule()` = filter by day, then sort. |
| Conflict handling | `Scheduler.detect_conflicts()` | Compares **time windows** (start + duration), not just identical start times. A sweep over time-sorted tasks keeps a list of still-running tasks, so each task is only compared to those. Returns readable warning strings and never raises. Checks across all pets, because one owner can't be in two places at once. |
| Recurring tasks | `Task.next_occurrence()`, `Pet.complete_task()`, `Scheduler.mark_task_complete()` | Completing a `daily`/`weekly` task adds a fresh copy due `due_date + timedelta(days=1 / weeks=1)`, moved forward past the completion date if it was finished late, so a weekly Monday task stays on Mondays. `once` tasks don't recur. Completing an already-completed task does nothing, so no duplicates are created. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
