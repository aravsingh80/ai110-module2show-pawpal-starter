# PawPal+ Project Reflection

## 1. System Design

**Core actions a user should be able to perform**

- A user should be able to add a pet or add multiple pets
- A user should be able to view their daily tasks
- A user should be able to schedule a task

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML design included four main classes: Owner, Pet, Task, and Scheduler. The Owner class represents the user and stores basic information like their name, email, available time per day, and the list of pets they own. It also includes methods for adding pets and checking how much time they have available. The Pet class represents each pet and stores details like its name, species, age, preferences, and the tasks assigned to it. It also has methods for adding tasks and getting tasks based on priority. The Task class represents activities like feeding or walking a pet, with attributes such as title, duration, priority, category, time of day, and whether the task is completed. It also includes methods for calculating priority and marking a task as complete. Finally, the Scheduler class organizes tasks across pets and generates a daily schedule while making sure the tasks fit within the owner’s available time.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, the design changed significantly during Phase 3. The initial `Task` class only had `title`, `duration_minutes`, `priority`, `category`, `time_of_day`, and `is_completed`. During implementation I added `start_time` (for time-based sorting and conflict detection), `frequency` and `due_date` (for recurring logic), and `pet_name` (for per-pet filtering). These were not in the original UML because I had not yet thought through the algorithmic layer — the initial design described *what* data to store but not *how* the scheduler would query or transform it. The final UML in `uml_final.md` reflects these additions along with the five new `Scheduler` methods.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers two constraints: the owner's **available time budget** (total minutes per day) and **task priority** (high / medium / low). Priority was treated as the primary constraint because it directly answers the user's most important question — "if I can't do everything, what should I definitely not skip?" Time budget is the hard ceiling: a task only enters the schedule if it fits within the remaining minutes. I deliberately left out preferences and time-of-day as hard constraints because enforcing them would require backtracking search, which is far more complex and harder to explain to a user.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

**Greedy priority-first scheduling ignores start times when fitting tasks into the day.**

The `generate_schedule` method sorts tasks by priority score and greedily adds each one until the time budget runs out. It does not consider `start_time` at all as a high-priority "Evening walk" could be scheduled before a low-priority "Morning medication" purely because of its priority rank, even if those times conflict in the real world.

This is a reasonable tradeoff for an MVP because most pet owners think first about *what must get done* rather than *exactly when*. Enforcing strict time ordering would require either rejecting tasks that don't fit their slot (surprising behavior) or doing full constraint-satisfaction search (far more complex). The separate `detect_conflicts` method handles the time-overlap problem explicitly, so the user gets a warning rather than the scheduler silently producing an impossible plan. The two concerns, "what to include" and "do any times clash", are kept intentionally separate for clarity.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

AI was used across every phase of this project. In Phase 1 it generated the initial Mermaid UML diagram from a plain-English description of the four classes, which gave me a concrete starting point rather than a blank page. In Phase 2 it produced the Python class skeletons and docstrings from that UML, saving the mechanical translation work. In Phase 3 I described the algorithmic features I wanted (sort by time, filter, recurring, conflict detection) and AI drafted implementations that I then reviewed, tested, and in one case rejected. For the UI wiring in Phase 4, AI helped translate backend method calls into Streamlit component patterns.

The most useful prompt pattern was providing context and a constraint together — e.g., "write a conflict detection method that returns warning strings rather than raising exceptions, so the UI can display them without crashing." Adding the *why* produced answers that fit the design rather than generic solutions.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

When asked to simplify `detect_conflicts`, AI suggested replacing the nested loop with `itertools.combinations`. The logic became: `for a, b in combinations(timed, 2): if to_minutes(a.start_time) < to_minutes(b.start_time) + b.duration_minutes and ...`. This was rejected because inlining four `to_minutes()` calls on one line made the overlap condition unreadable — especially for someone new to interval arithmetic. The original version with named variables `a_start`, `a_end`, `b_start`, `b_end` was kept because the extra four lines buy significant clarity. I verified my decision by asking: "could a classmate understand what this condition is testing without reading the docstring?" The named version passed that test; the combinations version did not.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

The 27-test suite covers: task completion and status flag, daily and weekly recurrence (including attribute preservation and missing `due_date` fallback), one-off tasks producing no next occurrence, priority scoring for all values including unknown, pet task management, chronological sorting with untimed tasks last, filtering by status and pet name, conflict detection (overlap, exact same time, and untimed-tasks-skipped), schedule generation respecting the time budget and priority order, and `mark_task_complete` with and without recurrence.

These tests matter because the scheduler's greedy algorithm and recurring logic interact in non-obvious ways — for example, completing a recurring task changes the pet's task list, which would affect the next call to `generate_schedule`. Without automated tests, a change to `mark_complete` could silently break recurrence without any visible error.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

Confidence level: ★★★★☆. All 27 unit tests pass and cover the core happy paths and most important edge cases. The remaining gap is integration testing: verifying that Streamlit session state persists correctly across multiple button clicks, testing multi-pet scenarios where two pets share the same owner's time budget, and testing what happens when `generate_schedule` is called multiple times in a session (the scheduler resets `scheduled_tasks` and `total_minutes_used` each call, but a test that confirms this would add confidence).

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The algorithmic layer in Phase 3 came together cleanly. Each method (`sort_by_time`, `filter_by_status`, `filter_by_pet`, `mark_task_complete`, `detect_conflicts`) has a single responsibility, a clear docstring, and a corresponding test. The decision to keep conflict detection separate from schedule generation — so the scheduler answers "what fits?" while `detect_conflicts` answers "do any times clash?" — kept both methods simple and independently testable.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

The `generate_schedule` algorithm is greedy and priority-only. In a real app, a pet owner might have a strict morning routine where the order of tasks matters as much as whether they're included. I would redesign `generate_schedule` to optionally accept a `respect_start_times` flag: when enabled, it would sort by `start_time` first and only fall back to priority for untimed tasks. I would also add multi-pet support so the Scheduler can handle an Owner with two pets sharing the same time budget.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The most important lesson was that **AI accelerates implementation but cannot replace architectural judgment**. AI could generate a `detect_conflicts` method in seconds, but it could not decide whether conflict detection should raise an exception, return a boolean, or return a list of strings — that decision depends on how the UI will consume the result, which only the architect knows. Every time AI produced a working solution that didn't fit the design (like the `combinations` version), the reason was that it optimized for code brevity without knowing the broader constraints. Being the "lead architect" meant deciding not just *what* to build, but *why* each piece is shaped the way it is.
