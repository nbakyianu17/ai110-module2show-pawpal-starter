from datetime import date
from pawpal_system import Task, Pet, Owner, Scheduler

# ── Setup ─────────────────────────────────────────────────────────────────────
jordan = Owner(name="Jordan", available_minutes=60)

mochi = Pet(name="Mochi", species="dog")
luna = Pet(name="Luna", species="cat")

# Tasks added out of order (sort_by_time will fix this)
mochi.add_task(Task("Evening walk",  duration_minutes=30, priority="medium", start_time="18:00", frequency="daily",  due_date=date.today()))
mochi.add_task(Task("Morning walk",  duration_minutes=20, priority="high",   start_time="08:00", frequency="daily",  due_date=date.today()))
mochi.add_task(Task("Flea treatment",duration_minutes=10, priority="high",   start_time="09:00", frequency="weekly", due_date=date.today()))

luna.add_task(Task("Clean litter box", duration_minutes=5,  priority="high",   start_time="08:00", frequency="daily",  due_date=date.today()))
luna.add_task(Task("Playtime",         duration_minutes=20, priority="medium", start_time="10:00", frequency="daily",  due_date=date.today()))
# Conflict: same start_time as Clean litter box
luna.add_task(Task("Give meds",        duration_minutes=5,  priority="high",   start_time="08:00", frequency="once",   due_date=date.today()))

jordan.add_pet(mochi)
jordan.add_pet(luna)

scheduler = Scheduler(owner=jordan)

# ── 1. Sort by time ───────────────────────────────────────────────────────────
print("=== Mochi's tasks sorted by time ===")
sorted_tasks = scheduler.sort_by_time(mochi.get_tasks())
for t in sorted_tasks:
    print(f"  {t.start_time}  {t.title}")

# ── 2. Filter tasks ───────────────────────────────────────────────────────────
print("\n=== Pending tasks for Luna ===")
luna_pending = scheduler.filter_tasks(pet_name="Luna", completed=False)
for t in luna_pending:
    print(f"  {t.title}")

# ── 3. Recurring tasks ────────────────────────────────────────────────────────
print("\n=== Recurring task demo ===")
morning_walk = mochi.get_tasks()[1]  # Morning walk
print(f"  Before: '{morning_walk.title}' due {morning_walk.due_date}, completed={morning_walk.completed}")
next_task = scheduler.mark_task_complete(morning_walk, mochi)
print(f"  After:  '{morning_walk.title}' completed={morning_walk.completed}")
if next_task:
    print(f"  Next occurrence added: '{next_task.title}' due {next_task.due_date}")

# ── 4. Conflict detection ─────────────────────────────────────────────────────
print("\n=== Conflict detection ===")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  WARNING: {warning}")
else:
    print("  No conflicts found.")

# ── 5. Daily plan ─────────────────────────────────────────────────────────────
print("\n")
plan = scheduler.generate_plan()
print(plan.explain())
