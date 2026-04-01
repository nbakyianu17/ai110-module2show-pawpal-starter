# PawPal+ (Module 2 Project)

**PawPal+** is a Python + Streamlit app that helps busy pet owners plan and track daily care tasks across multiple pets. You tell it how much time you have, add your pets and their tasks, and it builds a prioritised schedule — and tells you exactly why anything got left out.

## Features

### Pet and owner management
- Register an owner with a daily time budget (in minutes)
- Add multiple pets, each with their own task list
- Species support: dog, cat, or other

### Task tracking
- Each task has a title, duration, priority (low / medium / high), and frequency (daily / weekly / once)
- Optionally assign a start time (HH:MM) to any task
- Mark tasks complete; they won't appear in future plans until reset

### Priority-based scheduling
- The scheduler fits as many tasks as possible into the owner's available time
- Tasks are ranked high → medium → low, so the most important care always gets scheduled first
- Skipped tasks include a plain-English reason (e.g. "needs 30 min, only 15 min left")

### Chronological sorting
- Tasks with a start time are displayed in time order (earliest first)
- Tasks without a start time are sorted to the end — they won't clutter the timed view

### Conflict detection
- If two tasks on the same pet share the same start time, the app surfaces a visible warning immediately — no crashes, just a clear heads-up so you can fix it before generating the plan

### Recurring tasks
- Daily tasks automatically schedule their next occurrence for tomorrow when marked complete
- Weekly tasks roll forward by 7 days
- One-off tasks (`once`) are simply marked done with no follow-up created

### Filtering
- View only pending tasks, or only tasks for a specific pet — useful for multi-pet households

## Demo

<a href="/course_images/ai110/demo.png" target="_blank"><img src='/course_images/ai110/demo.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

<a href="/course_images/ai110/demo2.png" target="_blank"><img src='/course_images/ai110/demo2.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

## Smarter Scheduling

Beyond the basic daily plan, PawPal+ includes four algorithmic features:

- **Sort by time** — tasks can carry an optional `start_time` (HH:MM). `Scheduler.sort_by_time()` orders them chronologically using a lambda key, with untimed tasks falling to the end.
- **Filter tasks** — `Scheduler.filter_tasks()` accepts an optional pet name and/or completion status, making it easy to ask "what's still pending for Mochi?" without touching the rest of the task list.
- **Recurring tasks** — `Task` has a `frequency` field (`daily`, `weekly`, or `once`). Calling `Scheduler.mark_task_complete()` marks the task done and automatically adds the next occurrence to the pet's task list with the correct due date, calculated using `timedelta`.
- **Conflict detection** — `Scheduler.detect_conflicts()` scans each pet's timed tasks and returns a plain-English warning for any two tasks that share the same start time, without crashing the program.

## Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest tests/test_pawpal.py -v
```

The suite has 20 tests covering five areas:

- **Task completion** — `mark_complete()` and `reset()` change status correctly
- **Recurrence** — daily tasks get a next occurrence due tomorrow, weekly due in 7 days, and `"once"` tasks produce nothing
- **Sorting** — tasks sort chronologically by `start_time`; untimed tasks always go last
- **Conflict detection** — same-time tasks on the same pet trigger a warning; different times and missing times do not
- **Scheduling** — the plan respects the time budget, prioritises high-priority tasks, ignores completed tasks, and handles zero-budget and empty-pet edge cases

**Confidence level: ★★★★☆**

The core scheduling logic and edge cases are well covered. The main gap is the UI layer — there are no tests for how `app.py` wires the classes together, so a bug in the Streamlit integration wouldn't be caught automatically.

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
