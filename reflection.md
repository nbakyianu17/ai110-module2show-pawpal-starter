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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

The conflict detector only flags tasks that share the exact same `start_time` string — it doesn't calculate whether one task's duration overlaps into another's start time. For example, a 30-minute task at 08:00 and a task at 08:15 would not trigger a warning, even though they clearly overlap in real life.

I kept it this way because the alternative — computing end times and checking for interval overlap — adds a fair amount of logic for an edge case that mostly matters for tightly-packed schedules. For a pet care app where most tasks are short and spaced throughout the day, exact-match conflict detection catches the obvious mistakes (two things literally at the same time) without making the code hard to follow. If I were building this for a vet clinic with back-to-back appointments, the interval approach would be worth it.

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
