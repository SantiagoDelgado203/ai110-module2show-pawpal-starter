# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

1. **Add a pet** – The owner enters their own name and registers one or more pets (name, species, age) so PawPal+ knows who it is planning care for.
2. **Schedule a care task** – The owner adds a task for a specific pet, such as a walk, feeding, or medication, with a time of day, how long it takes, how important it is, and how often it repeats.
3. **See today's tasks** – The owner views a single, time-ordered schedule for the day that combines every pet's tasks, and can mark tasks as done as they go.

**a. Initial design**

My UML has four classes:

- **Task** (dataclass) – one care activity. Holds the description, time (`"HH:MM"`), duration, priority (low/medium/high), frequency (once/daily/weekly), and a completed flag. It is responsible for its own state: `mark_complete()` / `mark_incomplete()`, plus `priority_rank()` so other classes can compare priorities numerically.
- **Pet** (dataclass) – stores pet details (name, species, age) and owns its list of tasks. Responsible for adding/removing tasks and reporting its pending tasks and task count.
- **Owner** – the person using the app. Holds their name, how many minutes they have available for pet care, and a list of pets. Responsible for adding/removing/looking up pets and giving a flat view of every `(pet, task)` pair across all pets.
- **Scheduler** – the "brain." It holds a reference to an `Owner` and is responsible for pulling every task from the owner's pets, ordering them into today's schedule, and formatting that schedule for display.

Relationships: an Owner *has* many Pets (aggregation), a Pet *has* many Tasks (composition – a task does not exist without its pet), and the Scheduler *uses* an Owner rather than storing its own copy of the tasks.

**b. Design changes**

After drafting the skeleton I asked the AI assistant to review `pawpal_system.py` for missing relationships or bottlenecks. Changes I made based on that review:

- **Scheduler talks only to Owner.** My first idea was to give the Scheduler its own task list, but that would duplicate data and get out of sync when a task was added to a pet. Instead `Owner.get_all_tasks()` returns `(pet, task)` pairs and the Scheduler reads through it, so there is one source of truth.
- **Tasks don't store their pet; the schedule returns `(pet, task)` pairs.** The review pointed out that once tasks from several pets are merged into one schedule, you lose which pet each belongs to. Rather than add a back-reference from Task to Pet (a circular link), I kept Task simple and had the schedule carry the pet alongside each task.
- **Added `priority_rank()` to Task.** Priority is stored as a readable string, but sorting needs numbers. Putting the mapping on Task keeps that logic in one place instead of repeating it in the Scheduler and UI.

The design kept changing during implementation (compare `diagrams/uml.mmd` with `diagrams/uml_final.mmd`):

- **Added `due_date` to Task.** The draft only had a time of day. Recurring tasks need a *date* to move forward ("today + 1 day"), so `due_date` became a field and "today's schedule" became "filter by day, then sort."
- **Recurrence split across three classes.** `Task.next_occurrence()` only does the date math and returns a copy. `Pet.complete_task()` adds that copy to the pet's list, because the pet owns the list. `Scheduler.mark_task_complete()` is a convenience wrapper that finds a task by name. My first instinct was to put all of it in the Scheduler, but then the Scheduler would be changing a Pet's list behind its back.
- **Added a `PlanEntry` dataclass.** `build_plan()` needs to return "task + was it included + why." A small dataclass is clearer than a tuple of four values, and the UI can show the reason column directly.
- **Times are zero-padded on creation.** Without this, sorting `"8:00"` and `"07:30"` as strings put 8:00 first. Normalizing in `__post_init__` let `sort_by_time()` keep the simple string `lambda` key.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers:

- **Time of day.** Every task has a fixed `HH:MM` start time and a duration, and the daily view is ordered by time.
- **Due date and recurrence.** Only tasks due on the chosen day are shown, and daily/weekly tasks create their next occurrence when completed.
- **Priority** (low/medium/high). This breaks ties between tasks at the same time, and it decides what gets cut first when the owner doesn't have enough time.
- **The owner's available minutes.** The day's total is compared against this, and the UI warns when the plan doesn't fit.
- **Overlaps.** Tasks whose time windows overlap are flagged, even across different pets.

I decided time mattered most because pet care is mostly about routine. Feeding and medication happen at specific times, so a schedule that isn't in time order isn't useful. Priority comes second: it only matters when two things compete for the same slot or the same limited minutes.

**b. Tradeoffs**

**Conflicts produce warnings; the scheduler doesn't fix them.** `detect_conflicts()` returns warning strings and never moves, drops, or blocks a task. The owner decides what to do. A stricter scheduler could refuse overlapping tasks or move one automatically. But many "conflicts" are fine in real life: you can brush the cat while the dog eats. The owner knows that and the program doesn't. A warning keeps them informed without the app overriding their judgment.

**It checks overlapping time windows, not just exact start times.** This costs a little more work than comparing identical `HH:MM` strings: a sort plus a sweep over the "still-running" tasks instead of one dictionary lookup. But it catches the realistic case, like a 60-minute vet visit at 14:00 and a 14:30 walk. For a household with a handful of tasks a day, the extra cost doesn't matter.

**Recurrence keeps the original schedule.** When a recurring task is completed late, the next occurrence is based on the original due date, moved forward until it's after the completion date, rather than "completion date + interval." So a Monday task done late on Thursday comes back next Monday, which matches how people plan weekly care. The downside: a daily task completed a day late doesn't create a task for today, so the owner has to notice they missed a day.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code (an agent in the Claude desktop app) at every stage:

- **Design brainstorming.** I turned my list of classes, attributes, and methods into a Mermaid class diagram, then had the AI review the skeleton for missing relationships. That review is where the "Scheduler reads through Owner" and "`(pet, task)` pairs" decisions came from.
- **Scaffolding and implementation.** Agent mode wrote the dataclass skeletons and then the full implementation, editing `pawpal_system.py`, `main.py`, `app.py`, and the tests in one pass.
- **Algorithms.** I asked about using `sorted()` with a `lambda` key on `"HH:MM"` strings, how to use `timedelta` for recurrence, and for a "lightweight" conflict check that returns warnings instead of raising.
- **Testing and debugging.** I asked for a test plan covering happy paths and edge cases, then had the agent run `python -m pytest` and the CLI demo after each change.
- **Comparing models.** I gave the same recurrence prompt to two different models (see `ai_interactions.md`).

The most helpful prompts were **specific and constrained**. For example: "detect conflicts but return a warning string, never crash." Or: "a weekly task due Monday is completed Thursday; when is it due next?" Open-ended prompts like "make the scheduler smarter" gave long feature lists. Prompts with a concrete edge case gave code I could check right away.

**Most effective AI features:** agent mode for edits across several files (recurrence touched `Task`, `Pet`, `Scheduler`, `main.py`, and the tests at once), and letting the agent *run* the demo, the tests, and a headless Streamlit test. That meant I checked behavior, not just read code.

**b. Judgment and verification**

- **A rejected suggestion: flat overlap check.** The simplest conflict check suggested was to compare every pair of tasks with `itertools.combinations`. It's short and readable. But I wanted "back-to-back is not a conflict" and "only compare tasks that are still running." I kept the sorted sweep with an `active` list, which is about as readable and doesn't compare every pair. I checked it with three tests: same time, partial overlap, and back-to-back.
- **A modified suggestion: recurrence edge cases.** In the two-model comparison, one model's `complete()` had no guard against completing the same task twice, which would create duplicate future tasks. The other model used `<` instead of `<=` when rolling the date forward, so a daily task finished a day late would create a new task due *today*. I kept the "anchor on the original due date" idea that both models suggested. I added the already-completed guard in `Pet.complete_task()` and chose `<=`. `test_completing_twice_does_not_duplicate` and `test_late_weekly_completion_keeps_weekday` lock that in.
- **Keeping the design clean.** One idea was to give `Task` a reference back to its `Pet` so the schedule could show pet names. I said no because it creates a circular link that makes JSON saving harder. Returning `(pet, task)` pairs solved the same problem.
- **How I verified:** every change was followed by `python -m pytest` and `python main.py`. For the UI, I used Streamlit's `AppTest` to click through adding pets and tasks, conflicts, completing a task, and reloading from JSON, then opened the real app in a browser.

**Separate chat sessions.** I kept planning and building in separate conversations (Phases 1–3, then Phases 4–6), and ran the model comparison in separate, isolated agent contexts. Each session started from the current code, not a long chat history, so the AI wasn't working from outdated assumptions (for example, the Phase 1 version of `Task` with no `due_date`). Keeping the comparison isolated also meant neither model saw my implementation, so their answers were independent.

---

## 4. Testing and Verification

**a. What you tested**

31 tests in `tests/test_pawpal.py` cover:

- Task basics and validation (status changes, zero-padding, invalid input rejected)
- Chronological and priority sorting
- Filtering by pet, status, and day
- Daily and weekly recurrence (including late completion and double completion)
- Conflict detection (same time, overlap, back-to-back, other days)
- Next available slot, the time-budget plan, and JSON save/load
- The empty-household edge case

These matter because the scheduler's whole value is *trust*. If sorting is wrong, or a completed daily medication doesn't come back tomorrow, the owner could miss a dose. The recurrence and conflict tests guard the behaviors that would cause real problems if they broke quietly.

**b. Confidence**

**4 out of 5.** All core behaviors have both happy-path and edge-case tests, and they all pass. The UI was only checked with a scripted `AppTest` run and a manual browser check, not automated UI tests. If I had more time, I would test next:

- tasks that run past midnight (e.g., 23:30 for 60 min)
- editing or deleting a recurring task after its next copy already exists
- a very large number of tasks, for performance
- daylight-saving changes
- two tasks with the same description for the same pet, which `mark_task_complete` resolves by picking the earliest

---

## 5. Reflection

**a. What went well**

I'm most satisfied with the CLI-first structure. Because `pawpal_system.py` doesn't depend on Streamlit at all, every feature was proven in `main.py` and pytest before it reached the UI. Connecting it to Streamlit was mostly "call the method and display the result." Adding JSON persistence late in the project was also easy, because each class already owned its own data.

**b. What you would improve**

- Let users **edit and delete tasks** in the UI. Right now you can only add and complete them.
- Give each task a unique ID instead of looking it up by description.
- Make `build_plan()` smarter than greedy. For example, try to fill the time budget as fully as possible by importance (a knapsack problem), or move conflicting tasks automatically instead of only warning.
- Store owner preferences (e.g., "no walks after 21:00") as constraints the plan respects.

**c. Key takeaway**

Being the "lead architect" with a powerful AI means **owning the decisions, not the typing.** The AI could produce a working scheduler in minutes. The valuable work was deciding where responsibilities live (Task does date math, Pet owns its list, Scheduler only reads), spotting edge cases the AI didn't think of (duplicate spawns, `<` vs `<=`), and requiring every claim to be backed by a passing test. The clearer my design and constraints were, the better the AI's output got.
