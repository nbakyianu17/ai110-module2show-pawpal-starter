# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The three core actions a user should be able to perform:

1. **Register a pet and owner** — The user enters basic information about themselves (name, available time per day) and their pet (name, species). This gives the scheduler the context it needs to personalize the plan and respect time constraints.

2. **Add and manage care tasks** — The user defines what needs to happen each day: task name, how long it takes (in minutes), and how important it is (priority: low / medium / high). Tasks can be added before generating a schedule so the system has a complete picture of the day's needs.

3. **Generate and view today's schedule** — The user triggers the scheduler, which selects and orders tasks based on priority and time available, then displays the resulting plan along with a brief explanation of why each task was included and when it is scheduled.

I ended up with five classes. `Pet` and `Task` are simple dataclasses — they just hold data, no real behavior. `Pet` stores the pet's name and species. `Task` holds the task title, how long it takes, and its priority, plus a small helper `is_high_priority()` that the scheduler can call instead of comparing strings directly.

`Owner` is where the task list lives. It made sense to put `add_task`, `remove_task`, and `get_tasks` here since the owner is the one managing what needs to happen each day. The owner also holds a reference to their `Pet` and their `available_minutes`, which is the main time constraint.

`Scheduler` is the brain. It takes an `Owner` and uses everything on it — the task list, the time budget, the pet — to figure out what actually fits in the day. It produces a `DailyPlan`.

`DailyPlan` is the output. It stores which tasks made it in, which ones got cut, and how many minutes were used. The `explain()` method is responsible for turning that into something readable.

**b. Design changes**

When I reviewed the skeleton, I noticed that `skipped_tasks` was just a plain list of `Task` objects. That's a problem for `explain()` — if all you have is the task, you can't say *why* it was skipped (did it not fit in the time? was it low priority with nothing left?). So I added a `skipped_reasons` dict to `DailyPlan` that maps task titles to a short reason string. The `Scheduler` will populate this when it builds the plan. It's a small change but it makes `explain()` actually useful instead of just listing names.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers two constraints: time budget (how many minutes the owner has available) and task priority (high / medium / low). It also respects completion status — completed tasks are invisible to the scheduler so they don't crowd out things that still need doing.

Time budget came first because it's the hard constraint — you literally cannot do a 30-minute walk if you only have 20 minutes left. Priority is the tiebreaker that decides which tasks get the available time first. I didn't weight by frequency or species because those would add complexity without meaningfully improving the plan for a single-owner, single-day scenario.

**b. Tradeoffs**

The conflict detector only flags tasks that share the exact same `start_time` string — it doesn't calculate whether one task's duration overlaps into another's start time. For example, a 30-minute task at 08:00 and a task at 08:15 would not trigger a warning, even though they clearly overlap in real life.

I kept it this way because the alternative — computing end times and checking for interval overlap — adds a fair amount of logic for an edge case that mostly matters for tightly-packed schedules. For a pet care app where most tasks are short and spaced throughout the day, exact-match conflict detection catches the obvious mistakes (two things literally at the same time) without making the code hard to follow. If I were building this for a vet clinic with back-to-back appointments, the interval approach would be worth it.

---

## 3. AI Collaboration

**a. How you used AI**

AI was useful at almost every stage but in different ways depending on the phase. During design, it helped me think through what classes were needed and catch gaps — for example, it pointed out that `skipped_tasks` as a plain list gave `explain()` nothing to work with, which led to adding `skipped_reasons`. During implementation it was useful for boilerplate-heavy things like the dataclass setup and the `timedelta` recurrence logic, where getting the syntax right quickly let me focus on whether the logic was correct. For testing it was good at generating cases I hadn't thought of, like the zero-budget edge case and the empty-pet scenario.

The most effective prompts were specific and structural: "given this class, what's missing for this method to work?" got better answers than "how do I build a scheduler?" Anchoring questions to actual code rather than describing the problem in the abstract made the responses much more useful.

**b. Judgment and verification**

When I asked AI to simplify `filter_tasks()`, it suggested collapsing it into a nested list comprehension — shorter, more Pythonic, but genuinely harder to follow at a glance. The two `if` clauses at different levels of the comprehension aren't obvious to someone reading the code for the first time, and this method is one of the first things a new contributor would look at. I kept the explicit loop version. Readability isn't always about line count — sometimes the loop that spells out "filter pets, then filter tasks within each pet" is just clearer than the version that does both in one expression.

I evaluated it by reading both versions out loud. If I had to pause to mentally parse it, that was enough reason to keep the original.

---

## 4. Testing and Verification

**a. What you tested**

The 20 tests cover five areas: task completion and reset, recurrence logic (daily, weekly, and once), chronological sorting with and without start times, conflict detection (true positives, true negatives, and no-time edge case), and the scheduler itself (time budget, priority ordering, completed task exclusion, empty pet, zero budget).

The recurrence and conflict tests were the most important. Recurrence is stateful — completing a task changes the pet's task list — so a bug there could silently produce duplicate tasks or miss next occurrences entirely. Conflict detection needed both positive and negative cases because a detector that warns on everything is just as broken as one that warns on nothing.

**b. Confidence**

4 out of 5. The logic layer is thoroughly tested and behaved correctly in every case I tried. The gap is the Streamlit wiring — `app.py` has no automated tests, so a session state bug or a broken button handler wouldn't be caught until someone ran the app manually. If I had more time I'd add edge cases for: tasks whose duration exactly equals the remaining budget (boundary condition), an owner with no pets at all, and a pet that has only completed tasks.

---

## 5. Reflection

**a. What went well**

The separation between the logic layer and the UI ended up being the best structural decision. Because `pawpal_system.py` knew nothing about Streamlit, I could test all the scheduling behavior in isolation, run `main.py` as a quick terminal demo, and then wire everything into the app without touching the logic. When a UI button wasn't working right, the problem was always in `app.py` — never in the scheduler — which made debugging straightforward.

**b. What you would improve**

The greedy scheduling algorithm works but it's naive — it locks in the first high-priority task it sees and won't backtrack even if a different combination of lower-priority tasks would use the time budget more efficiently. For most pet care scenarios this doesn't matter, but a smarter approach would try to maximise total tasks completed (a knapsack-style problem) rather than just filling time in priority order. I'd also add a proper `due_date` filter so the scheduler only considers tasks that are actually due today, not every task ever added to a pet.

**c. Key takeaway**

AI is fast at generating code but it has no idea what your system is supposed to feel like from the inside. It will suggest the most compact or "Pythonic" solution to the immediate question without considering how that fits into the broader design — whether the naming is consistent, whether a new class is really needed, or whether a simpler structure already handles the case. The value I added wasn't writing faster than AI could; it was knowing when to say "that's technically correct but it doesn't belong here." Being the lead architect means making those calls, not just accepting whatever gets generated.
