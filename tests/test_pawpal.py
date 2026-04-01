from datetime import date, timedelta
import pytest
from pawpal_system import Task, Pet, Owner, Scheduler, DailyPlan


# helpers
def make_owner(minutes=60):
    return Owner(name="Jordan", available_minutes=minutes)

def make_scheduler(minutes=60):
    owner = make_owner(minutes)
    pet = Pet(name="Mochi", species="dog")
    owner.add_pet(pet)
    return owner, pet, Scheduler(owner)


# ── Task completion ────────────────────────────────────────────────────────────

def test_mark_complete_changes_status():
    task = Task(title="Walk", duration_minutes=20, priority="high")
    task.mark_complete()
    assert task.completed is True

def test_reset_clears_completed():
    task = Task(title="Walk", duration_minutes=20, priority="high", completed=True)
    task.reset()
    assert task.completed is False


# ── Recurrence logic ───────────────────────────────────────────────────────────

def test_daily_task_next_occurrence_is_tomorrow():
    today = date.today()
    task = Task(title="Walk", duration_minutes=20, priority="high", frequency="daily", due_date=today)
    next_task = task.generate_next_occurrence()
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)

def test_weekly_task_next_occurrence_is_seven_days():
    today = date.today()
    task = Task(title="Bath", duration_minutes=30, priority="medium", frequency="weekly", due_date=today)
    next_task = task.generate_next_occurrence()
    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)

def test_once_task_generates_no_next_occurrence():
    task = Task(title="Vet visit", duration_minutes=60, priority="high", frequency="once")
    assert task.generate_next_occurrence() is None

def test_mark_task_complete_adds_next_to_pet():
    owner, pet, scheduler = make_scheduler()
    task = Task(title="Walk", duration_minutes=20, priority="high", frequency="daily", due_date=date.today())
    pet.add_task(task)
    scheduler.mark_task_complete(task, pet)
    assert task.completed is True
    assert len(pet.get_tasks()) == 2
    assert pet.get_tasks()[1].due_date == date.today() + timedelta(days=1)

def test_mark_task_complete_once_does_not_add_to_pet():
    owner, pet, scheduler = make_scheduler()
    task = Task(title="Vet visit", duration_minutes=60, priority="high", frequency="once")
    pet.add_task(task)
    scheduler.mark_task_complete(task, pet)
    assert len(pet.get_tasks()) == 1


# ── Sorting ────────────────────────────────────────────────────────────────────

def test_sort_by_time_returns_chronological_order():
    owner, pet, scheduler = make_scheduler()
    tasks = [
        Task(title="Evening walk", duration_minutes=30, priority="low",    start_time="18:00"),
        Task(title="Meds",         duration_minutes=5,  priority="high",   start_time="08:00"),
        Task(title="Playtime",     duration_minutes=15, priority="medium", start_time="12:00"),
    ]
    result = scheduler.sort_by_time(tasks)
    assert [t.start_time for t in result] == ["08:00", "12:00", "18:00"]

def test_sort_by_time_untimed_tasks_go_last():
    owner, pet, scheduler = make_scheduler()
    tasks = [
        Task(title="No time",  duration_minutes=10, priority="high"),
        Task(title="Morning",  duration_minutes=20, priority="high", start_time="07:00"),
    ]
    result = scheduler.sort_by_time(tasks)
    assert result[0].start_time == "07:00"
    assert result[1].start_time is None

def test_sort_by_time_empty_list():
    owner, pet, scheduler = make_scheduler()
    assert scheduler.sort_by_time([]) == []


# ── Conflict detection ─────────────────────────────────────────────────────────

def test_detect_conflicts_flags_same_start_time():
    owner, pet, scheduler = make_scheduler()
    pet.add_task(Task(title="Walk",  duration_minutes=20, priority="high",   start_time="08:00"))
    pet.add_task(Task(title="Meds",  duration_minutes=5,  priority="high",   start_time="08:00"))
    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1
    assert "08:00" in warnings[0]

def test_detect_conflicts_no_warning_for_different_times():
    owner, pet, scheduler = make_scheduler()
    pet.add_task(Task(title="Walk",  duration_minutes=20, priority="high", start_time="08:00"))
    pet.add_task(Task(title="Meds",  duration_minutes=5,  priority="high", start_time="09:00"))
    assert scheduler.detect_conflicts() == []

def test_detect_conflicts_no_warning_when_no_start_times():
    owner, pet, scheduler = make_scheduler()
    pet.add_task(Task(title="Walk", duration_minutes=20, priority="high"))
    pet.add_task(Task(title="Meds", duration_minutes=5,  priority="high"))
    assert scheduler.detect_conflicts() == []


# ── Scheduler: generate_plan ───────────────────────────────────────────────────

def test_generate_plan_respects_time_budget():
    owner, pet, scheduler = make_scheduler(minutes=30)
    pet.add_task(Task(title="Long walk", duration_minutes=25, priority="high"))
    pet.add_task(Task(title="Bath",      duration_minutes=20, priority="medium"))
    plan = scheduler.generate_plan()
    assert plan.total_minutes_used <= 30

def test_generate_plan_schedules_high_priority_first():
    owner, pet, scheduler = make_scheduler(minutes=20)
    low  = Task(title="Brush", duration_minutes=15, priority="low")
    high = Task(title="Meds",  duration_minutes=15, priority="high")
    pet.add_task(low)
    pet.add_task(high)
    plan = scheduler.generate_plan()
    assert high in plan.scheduled_tasks
    assert low in plan.skipped_tasks

def test_generate_plan_skips_completed_tasks():
    owner, pet, scheduler = make_scheduler()
    done = Task(title="Walk", duration_minutes=20, priority="high", completed=True)
    pet.add_task(done)
    plan = scheduler.generate_plan()
    assert done not in plan.scheduled_tasks

def test_generate_plan_empty_pet_returns_empty_plan():
    owner, pet, scheduler = make_scheduler()
    plan = scheduler.generate_plan()
    assert plan.scheduled_tasks == []
    assert plan.total_minutes_used == 0

def test_generate_plan_zero_budget_skips_everything():
    owner, pet, scheduler = make_scheduler(minutes=0)
    pet.add_task(Task(title="Walk", duration_minutes=20, priority="high"))
    plan = scheduler.generate_plan()
    assert plan.scheduled_tasks == []
    assert len(plan.skipped_tasks) == 1


# ── Filtering ──────────────────────────────────────────────────────────────────

def test_filter_by_pet_name_returns_only_that_pets_tasks():
    owner = make_owner()
    mochi = Pet(name="Mochi", species="dog")
    luna  = Pet(name="Luna",  species="cat")
    mochi.add_task(Task(title="Walk",        duration_minutes=20, priority="high"))
    luna.add_task( Task(title="Litter box",  duration_minutes=5,  priority="high"))
    owner.add_pet(mochi)
    owner.add_pet(luna)
    scheduler = Scheduler(owner)
    result = scheduler.filter_tasks(pet_name="Mochi")
    assert all(t.title == "Walk" for t in result)
    assert len(result) == 1

def test_filter_by_completed_excludes_done_tasks():
    owner, pet, scheduler = make_scheduler()
    done    = Task(title="Done task",    duration_minutes=10, priority="low",  completed=True)
    pending = Task(title="Pending task", duration_minutes=10, priority="high")
    pet.add_task(done)
    pet.add_task(pending)
    result = scheduler.filter_tasks(completed=False)
    assert pending in result
    assert done not in result
