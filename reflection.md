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

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
