# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

**What task did you give the agent?**

I used Claude Code in agent mode with this goal: *"Complete Phases 4–6 plus the optional extensions."* That meant adding sorting, filtering, recurring tasks, and conflict detection to the Scheduler; a third algorithm beyond the basics; JSON persistence; priority-first scheduling; nicer CLI/UI output; a full pytest suite; showing all of it in the Streamlit UI; and updating the UML, README, and reflection. I asked for a commit and push to `main` at the end of each phase.

**What did the agent do?**

| Step | Files modified | What was completed |
|------|----------------|--------------------|
| 1. Algorithmic layer (Phase 4) | `pawpal_system.py`, `main.py`, `README.md`, `reflection.md` | Added `due_date` to `Task`; `sort_by_time`, `filter_tasks`, `get_todays_schedule`; `Task.next_occurrence` + `Pet.complete_task` + `Scheduler.mark_task_complete` for daily/weekly recurrence with `timedelta`; `detect_conflicts` (overlap sweep). Updated the demo to add tasks out of order, with two at the same time. Committed as `feat: implement sorting, filtering, and conflict detection`. |
| 2. Extensions | `pawpal_system.py`, `main.py`, `.gitignore` | **Third algorithm:** `find_next_available_slot` (gap search) and `build_plan` (greedy priority plan within the owner's time budget, returning `PlanEntry` objects with reasons). **Priority scheduling:** `sort_by_priority`. **Persistence:** `to_dict`/`from_dict` on each class, `Owner.save_to_json` / `load_from_json`. **Formatting:** `Task.emoji()`, ✅/⬜ status markers, ANSI priority colors. |
| 3. Test suite (Phase 5) | `tests/test_pawpal.py`, `README.md` | Grew from 3 to 31 tests using a fixed date and a `household` fixture. Ran `python -m pytest`: 31 passed. Committed as `test: add automated test suite for PawPal+ system`. |
| 4. UI polish (Phase 6) | `app.py`, `requirements.txt` | Sidebar owner/pet management, a Schedule tab (filters, sort toggle, `st.dataframe`, `st.metric`, conflict `st.warning`, complete button that shows the next occurrence), an Add-task tab with a "next free slot" option, a Smart-plan tab, and load/save to `data.json`. |
| 5. Docs | `diagrams/uml_final.mmd`, `README.md`, `reflection.md`, `ai_interactions.md` | Final UML; README Features / Smarter Scheduling / Challenge sections / Demo Walkthrough with real CLI output; reflection sections 1b and 2–5. |

Verification the agent ran along the way: `python main.py` after each backend change, `python -m pytest` after each change, a scripted Streamlit `AppTest` run (add pets → add conflicting tasks → auto-slot → complete a task → reload from JSON in a new session), and loading the real app in the built-in browser.

**What did you have to verify or fix manually?**

These problems were caught by reviewing output, not by the first draft:

- **Emoji keyword gap.** In the first demo run, "Fetch in the yard" showed the generic 🐾 because "fetch" wasn't a play keyword. I added it.
- **Misleading plan reason.** A skipped task said "only 0 min left *after higher-priority tasks*," but the time had gone to a task with the *same* priority. I changed the wording to "left in the budget."
- **Unsorted filter output.** The first "only Luna's tasks" demo printed in insertion order. I wrapped it in `sort_by_time()`.
- **Windows encoding.** Printing emojis failed with `UnicodeEncodeError` when output was redirected (cp1252). `main.py` now calls `sys.stdout.reconfigure(encoding="utf-8")`.
- **Streamlit deprecation.** `use_container_width=True` printed deprecation warnings on Streamlit 1.60, so I replaced it with `width="stretch"` and raised the requirement to `streamlit>=1.50`.
- **Stale server.** The first browser check showed `Owner has no attribute load_from_json`. An older Streamlit process on port 8501 still had the old module loaded. It wasn't a code bug: restarting on a new port fixed it. Lesson: restart Streamlit after changing imported modules.
- **Recurrence edge cases** from the model comparison below (`<` vs `<=`, the duplicate-completion guard). I reviewed these myself and pinned them with tests.

---

## Prompt Comparison (SF11)

**Task:** the logic for rescheduling recurring (daily/weekly) tasks when they're completed, including a weekly task completed *late*.

Both models got the identical prompt in a fresh, isolated context with no access to my code. The prompt included the `Task` dataclass (with `due_date`) and asked for code using `timedelta`, a decision on whether to anchor the next date to the original due date or the completion date, and where the logic should live (Task vs. Pet vs. Scheduler).

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | Claude Sonnet (Claude Code subagent) | Claude Haiku (Claude Code subagent) |
| **Prompt** | Same prompt for both (summarized above) | Same prompt for both |
| **Response summary** | Put the date math inside `Task.mark_complete(today)`, which returns the next `Task` (made with `dataclasses.replace`). The Scheduler appends it to `pet.tasks`. Anchored on the original `due_date` and rolled forward with `while next_due < today`. | Added a separate `Task.complete(completed_on)` that returns the next `Task`, and `Pet.complete_task()` appends it. Also anchored on `due_date`, but rolled forward with `while next_due <= today`. Argued the Scheduler should only sort, filter, and report. |
| **What was useful** | Clear reason to anchor on the due date (otherwise a Monday task drifts to Thursday forever). **Included an "already completed → return None" guard** so tasks can't be spawned twice. Used `replace()` so the original stays as history. | **Put list ownership in `Pet`**, matching my design. Used `<=`, so a late daily task doesn't create one due today. Noted a real-world caveat: for medications that must happen every day, skipping missed days might not be what an owner wants. |
| **Problems noticed** | `<` means a daily task due yesterday and finished today creates a new task due *today*, which might double-count. Gave the Scheduler the job of changing a Pet's list, so the Scheduler reaches into Pet's data. | **No guard against completing twice.** Calling `complete()` on an already-completed task creates a second future copy, so the same day could have duplicate walks. |
| **Decision** | Kept: the duplicate-completion guard and the due-date anchor. | Kept: `<=` rolling, and `Pet` owning the append. |

**Which approach did you use in your final implementation and why?**

A combination of both. `Task.next_occurrence(completed_on)` only does the date math (anchored on `due_date`, rolled forward with `<=` as in Option B) and doesn't change the task. `Pet.complete_task()` owns the list, as in Option B. It marks the task complete, adds the next occurrence, and has the "already completed" guard from Option A. Keeping `next_occurrence()` free of side effects made it easy to unit test, and putting the guard where the list is changed means no caller can create duplicates. Both choices are covered by tests (`test_completing_twice_does_not_duplicate`, `test_late_weekly_completion_keeps_weekday`). Neither model's code was perfect alone. Comparing them is what exposed each one's blind spot.
