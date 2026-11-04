# 🐾 PawPal+ (Module 2 Project)

**PawPal+** is a smart pet care planner built with Python and Streamlit. It helps a busy owner track feedings, walks, medications, and appointments for several pets. It puts the day in order, flags conflicts, repeats routine tasks automatically, and explains which tasks fit in the time the owner has.

The project followed a CLI-first workflow. The logic layer (`pawpal_system.py`) was designed in UML, built and checked with a terminal demo (`main.py`) and a pytest suite, and only then connected to the Streamlit UI (`app.py`).

## ✨ Features

- **Multi-pet households.** One owner, any number of pets, each with its own task list.
- **Sorting by time.** The daily schedule is always in chronological order across all pets (`Scheduler.sort_by_time`).
- **Priority-based sorting.** Optionally sort high → medium → low priority, with time as the tie-breaker (`Scheduler.sort_by_priority`).
- **Filtering.** By pet, by completion status (pending/done), and by day; filters can be combined (`Scheduler.filter_tasks`).
- **Daily & weekly recurrence.** Completing a recurring task automatically creates its next occurrence using `timedelta`. A late completion keeps the original weekday (`Task.next_occurrence`, `Pet.complete_task`).
- **Conflict warnings.** Detects tasks whose time windows overlap, not just identical start times, even across different pets. Shows a friendly warning instead of crashing (`Scheduler.detect_conflicts`).
- **Next available slot.** Finds the earliest free gap of a given length in the day (`Scheduler.find_next_available_slot`).
- **Smart daily plan.** Picks which pending tasks fit in the owner's available minutes, highest priority first, and explains each choice (`Scheduler.build_plan`).
- **Data persistence.** Pets and tasks are saved to `data.json` and reloaded the next time you open the app (`Owner.save_to_json` / `Owner.load_from_json`).
- **Readable output.** Emoji task-type icons, ✅/⬜ status markers, color-coded priority badges in the UI, and ANSI-colored priorities in the terminal.

## 🚀 Getting started

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

| Command | What it does |
|---------|--------------|
| `streamlit run app.py` | Launch the web app |
| `python main.py` | Run the CLI demo of every scheduler feature |
| `python -m pytest` | Run the automated test suite |

### Project structure

```
pawpal_system.py        # Logic layer: Task, Pet, Owner, Scheduler, PlanEntry
app.py                  # Streamlit UI, wired to the logic layer
main.py                 # CLI demo script
tests/test_pawpal.py    # pytest suite (31 tests)
diagrams/uml.mmd        # Phase 1 draft UML
diagrams/uml_final.mmd  # Final UML matching the code
reflection.md           # Design + AI collaboration reflection
ai_interactions.md      # Agent workflow + prompt comparison (stretch features)
```

## 🖥️ Sample Output

Output of `python main.py`:

```
### Today's schedule (sorted by time)
Schedule for Jordan - Wednesday, Nov 04
================================================================
  ⬜ 07:30  🦮 Mochi   Morning walk       30 min  high   daily
  ⬜ 08:00  🍖 Luna    Breakfast          10 min  high   daily
  ⬜ 12:00  💊 Luna    Flea medication     5 min  high   weekly
  ⬜ 14:00  🩺 Mochi   Vet appointment    60 min  medium once
  ⬜ 14:00  🛁 Luna    Brush fur          15 min  low    weekly
  ⬜ 16:00  🎾 Mochi   Fetch in the yard  20 min  low    daily
  ⬜ 18:30  🦮 Mochi   Evening walk       30 min  medium daily
----------------------------------------------------------------
  7 tasks, 170 min total (120 min available)

### Sorted by priority, then time
  ⬜ 07:30  🦮 Mochi   Morning walk       30 min  high   daily
  ⬜ 08:00  🍖 Luna    Breakfast          10 min  high   daily
  ⬜ 12:00  💊 Luna    Flea medication     5 min  high   weekly
  ⬜ 14:00  🩺 Mochi   Vet appointment    60 min  medium once
  ⬜ 18:30  🦮 Mochi   Evening walk       30 min  medium daily
  ⬜ 14:00  🛁 Luna    Brush fur          15 min  low    weekly
  ⬜ 16:00  🎾 Mochi   Fetch in the yard  20 min  low    daily

### Filter: only Luna's tasks
  ⬜ 08:00  🍖 Luna    Breakfast          10 min  high   daily
  ⬜ 12:00  💊 Luna    Flea medication     5 min  high   weekly
  ⬜ 14:00  🛁 Luna    Brush fur          15 min  low    weekly

### Conflict check
  ⚠️  Conflict (same time): 14:00 Mochi - Vet appointment (60 min) and 14:00 Luna - Brush fur (15 min)

### Daily plan within 120 available minutes
  ✔ 07:30 Mochi  Morning walk      high priority; fits (30/120 min used)
  ✔ 08:00 Luna   Breakfast         high priority; fits (40/120 min used)
  ✔ 12:00 Luna   Flea medication   high priority; fits (45/120 min used)
  ✔ 14:00 Mochi  Vet appointment   medium priority; fits (105/120 min used)
  ✔ 14:00 Luna   Brush fur         low priority; fits (120/120 min used)
  ✘ 16:00 Mochi  Fetch in the yard skipped: needs 20 min, only 0 min left in the budget
  ✘ 18:30 Mochi  Evening walk      skipped: needs 30 min, only 15 min left in the budget

### Next available slot
   30-minute task fits at: 07:00
   90-minute task fits at: 08:10

### Recurring tasks: completing Morning walk and Flea medication
  Morning walk done -> next occurrence Thu Nov 05 at 07:30
  Flea medication done -> next occurrence Wed Nov 11 at 12:00
  Vet appointment done -> next occurrence: None

### Filter: tasks still pending today
  ⬜ 08:00  🍖 Luna    Breakfast          10 min  high   daily
  ⬜ 14:00  🛁 Luna    Brush fur          15 min  low    weekly
  ⬜ 16:00  🎾 Mochi   Fetch in the yard  20 min  low    daily
  ⬜ 18:30  🦮 Mochi   Evening walk       30 min  medium daily

### Tomorrow's schedule
Schedule for Jordan - Thursday, Nov 05
================================================================
  ⬜ 07:30  🦮 Mochi   Morning walk       30 min  high   daily
----------------------------------------------------------------
  1 task, 30 min total (120 min available)

### Persistence: save to JSON and load it back
  Saved and reloaded 2 pets with 9 tasks; matches original: True
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
| Priority sorting | `Scheduler.sort_by_priority()` | Key `(-priority_rank, due_date, time)`: high first, then earliest. |
| Filtering | `Scheduler.filter_tasks(pet_name=, completed=, day=)` | Each filter is optional, and filters combine (e.g. pending tasks for Luna today). `get_todays_schedule()` = filter by day, then sort. |
| Conflict handling | `Scheduler.detect_conflicts()` | Compares **time windows** (start + duration), not just identical start times. A sweep over time-sorted tasks keeps a list of still-running tasks, so each task is only compared to those. Returns readable warning strings and never raises. Checks across all pets, because one owner can't be in two places at once. |
| Recurring tasks | `Task.next_occurrence()`, `Pet.complete_task()`, `Scheduler.mark_task_complete()` | Completing a `daily`/`weekly` task adds a fresh copy due `due_date + timedelta(days=1 / weeks=1)`, moved forward past the completion date if it was finished late, so a weekly Monday task stays on Mondays. `once` tasks don't recur. Completing an already-completed task does nothing, so no duplicates are created. |
| Next available slot | `Scheduler.find_next_available_slot()` | Moves a cursor through the day's tasks in time order and returns the first gap long enough for the task (default window 07:00–22:00), or `None`. |
| Daily plan | `Scheduler.build_plan()` → `list[PlanEntry]` | Greedy by priority within `owner.available_minutes`. Each entry records whether the task was included and a human-readable reason. |

### Advanced priority scheduling (Challenge 3)

`Task.priority` is a validated `low` / `medium` / `high` level, and `Task.priority_rank()` turns it into a number for sorting. `Scheduler.sort_by_priority()` sorts by priority first, then by time. `Scheduler.build_plan()` uses that order to decide which tasks fit in the owner's time budget. Excerpt from `python main.py`:

```
### Sorted by priority, then time
  ⬜ 07:30  🦮 Mochi   Morning walk       30 min  high   daily
  ⬜ 08:00  🍖 Luna    Breakfast          10 min  high   daily
  ⬜ 12:00  💊 Luna    Flea medication     5 min  high   weekly
  ⬜ 14:00  🩺 Mochi   Vet appointment    60 min  medium once
  ⬜ 18:30  🦮 Mochi   Evening walk       30 min  medium daily
  ⬜ 14:00  🛁 Luna    Brush fur          15 min  low    weekly
  ⬜ 16:00  🎾 Mochi   Fetch in the yard  20 min  low    daily

### Daily plan within 120 available minutes
  ✔ 07:30 Mochi  Morning walk      high priority; fits (30/120 min used)
  ✔ 08:00 Luna   Breakfast         high priority; fits (40/120 min used)
  ✔ 12:00 Luna   Flea medication   high priority; fits (45/120 min used)
  ✔ 14:00 Mochi  Vet appointment   medium priority; fits (105/120 min used)
  ✔ 14:00 Luna   Brush fur         low priority; fits (120/120 min used)
  ✘ 16:00 Mochi  Fetch in the yard skipped: needs 20 min, only 0 min left in the budget
  ✘ 18:30 Mochi  Evening walk      skipped: needs 30 min, only 15 min left in the budget
```

Note that **Evening walk** (medium, 30 min) is skipped while **Brush fur** (low, 15 min) is kept. The walk was considered first, but by then only 15 minutes were left, and the shorter brushing task still fit. Every skipped task says why.

### Data persistence (Challenge 2)

- **Files modified:** `pawpal_system.py` (added `to_dict` / `from_dict` to `Task`, `Pet`, and `Owner`, plus `Owner.save_to_json()` and `Owner.load_from_json()`), `app.py` (load on startup, save after every change), `.gitignore` (ignores `data.json`), and `tests/test_pawpal.py` (round-trip tests).
- **Workflow:**
  1. When a Streamlit session starts, `app.py` calls `Owner.load_from_json("data.json")`. If the file doesn't exist it returns `None`, and the app starts with a new empty owner.
  2. Every action that changes data (add pet, add task, complete task, edit owner) calls `owner.save_to_json()`.
  3. Each class handles its own conversion with a custom dictionary method (no extra library needed). Dates are stored as ISO strings (`"2026-11-04"`) and parsed back with `date.fromisoformat`.
  4. **Reset all data** in the sidebar deletes `data.json`. You can set the `PAWPAL_DATA_FILE` environment variable to use a different file.

### Output formatting (Challenge 4)

| Feature | Where | How |
|---------|-------|-----|
| Task-type emojis (🦮 walk, 🍖 food, 💊 meds, 🩺 vet, 🛁 grooming, 🎾 play, 🧹 cleaning, 🐾 other) | `Task.emoji()` | Keyword match on the description, using the `TASK_EMOJIS` table |
| ✅ / ⬜ status markers and aligned columns | `Scheduler.format_row()`, `format_schedule()` | f-string padding (`:<17`, `:>3`) |
| Colored priorities in the terminal (red / yellow / green) | `format_row(color=True)` | ANSI escape codes. `main.py` only turns them on when output goes to a real terminal and `NO_COLOR` isn't set. |
| Color badges 🔴 🟡 🟢, `st.dataframe` tables, `st.metric` cards, `st.warning` / `st.success` messages | `app.py` | Streamlit components |

No third-party formatting library was needed. Everything uses f-strings and the standard library, and `main.py` switches stdout to UTF-8 so emojis print on Windows.

## 🏗️ Architecture

The final class diagram is in [`diagrams/uml_final.mmd`](diagrams/uml_final.mmd); the Phase 1 draft is in [`diagrams/uml.mmd`](diagrams/uml.mmd).

- `Owner` **owns** many `Pet`s, and each `Pet` **has** many `Task`s.
- `Scheduler` holds no data of its own. It reads every task through `Owner.get_all_tasks()`, which returns `(pet, task)` pairs, so there is one source of truth.
- Recurrence is split by responsibility: `Task.next_occurrence()` does the date math, `Pet.complete_task()` adds the new task to the pet's list, and `Scheduler.mark_task_complete()` is the convenient entry point that looks a task up by name.
- `build_plan()` returns `PlanEntry` objects (pet, task, included, reason) so the UI can explain its choices.

## 📸 Demo Walkthrough

**Main UI features.** The **sidebar** holds the owner's name and daily minutes available, an **Add a pet** form, a list of your pets with their pending-task counts, and a **Reset all data** button. The main area has a **📅 Day** picker and three tabs:

- **📋 Schedule.** A table of that day's tasks with emoji, time, pet, duration, priority badge, and repeat setting. You can filter by pet and status, sort by time or priority, and see metric cards (tasks, minutes planned vs. available, minutes done). There is also a **Mark a task complete** control.
- **➕ Add task.** A form for pet, description, date, time, duration, priority, and repeat setting. A **"Use the next free slot"** checkbox picks the time for you, and a hint line shows the next free 15/30/60-minute slots.
- **🧠 Smart plan.** Shows which pending tasks fit in your available minutes, with a ✔️/✖️ and a "Why" column for each.

**Example workflow:**

1. Run `streamlit run app.py`. With no data yet, the app asks you to add a pet in the sidebar.
2. In the sidebar, set the owner name to *Jordan* and minutes available to *120*. Add **Mochi** (dog, 3) and then **Luna** (cat, 5). Each one shows a success message and appears under "Your pets."
3. Open **➕ Add task**. Schedule *Morning walk* for Mochi at 07:30, 30 min, high, daily. Then schedule *Breakfast* for Luna at 07:30. The second task is saved, but the message turns into a ⚠️ warning saying it overlaps another task.
4. Open **📋 Schedule**. Both tasks are listed in time order, and a yellow banner at the top explains the conflict ("You can't be in two places at once…") with both tasks' times and durations.
5. Back in **➕ Add task**, add *Brush fur* for Luna with **"Use the next free slot"** ticked. PawPal+ places it in the first gap that fits.
6. In **📋 Schedule**, choose *Morning walk* under **Mark a task complete** and click **✅ Complete**. The success message says a new daily copy was added for tomorrow. Change the **📅 Day** picker to tomorrow to see it.
7. Set the status filter to **Pending** or pick a single pet to narrow the table, or switch **Sort by** to **Priority**.
8. Open **🧠 Smart plan**. If tasks add up to more than your available minutes, a warning lists what doesn't fit, and the table explains each decision.
9. Close the browser and run the app again. Your pets and tasks reload from `data.json`.

**Key Scheduler behaviors shown:** chronological sorting across pets, priority sorting, pet/status filtering, overlap-based conflict warnings, automatic daily/weekly recurrence, next-free-slot placement, and a time-budget plan with reasons.

**CLI demo** (`python main.py`, excerpt; full output is in [Sample Output](#️-sample-output)):

```
### Today's schedule (sorted by time)
Schedule for Jordan - Wednesday, Nov 04
================================================================
  ⬜ 07:30  🦮 Mochi   Morning walk       30 min  high   daily
  ⬜ 08:00  🍖 Luna    Breakfast          10 min  high   daily
  ⬜ 12:00  💊 Luna    Flea medication     5 min  high   weekly
  ⬜ 14:00  🩺 Mochi   Vet appointment    60 min  medium once
  ⬜ 14:00  🛁 Luna    Brush fur          15 min  low    weekly
  ⬜ 16:00  🎾 Mochi   Fetch in the yard  20 min  low    daily
  ⬜ 18:30  🦮 Mochi   Evening walk       30 min  medium daily
----------------------------------------------------------------
  7 tasks, 170 min total (120 min available)

### Conflict check
  ⚠️  Conflict (same time): 14:00 Mochi - Vet appointment (60 min) and 14:00 Luna - Brush fur (15 min)

### Recurring tasks: completing Morning walk and Flea medication
  Morning walk done -> next occurrence Thu Nov 05 at 07:30
  Flea medication done -> next occurrence Wed Nov 11 at 12:00
  Vet appointment done -> next occurrence: None

### Next available slot
   30-minute task fits at: 07:00
   90-minute task fits at: 08:10
```
