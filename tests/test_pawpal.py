from pawpal_system import Task, Pet


def test_mark_complete_changes_status():
    task = Task(title="Morning walk", duration_minutes=20, priority="high")
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog")
    task = Task(title="Feed", duration_minutes=5, priority="medium")
    pet.add_task(task)
    assert len(pet.get_tasks()) == 1
