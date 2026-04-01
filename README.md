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
