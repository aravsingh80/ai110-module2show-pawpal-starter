from pawpal_system import Task, Pet

def test_mark_complete():
    # create a task
    task = Task("Feed Dog", 10, "medium", "feeding", "morning", False)

    # mark it complete
    task.mark_complete()

    # verify status changed
    assert task.is_completed == True


def test_add_task_to_pet():
    # create pet
    pet = Pet("Buddy", "Dog", 3, [], [])

    # create task
    task = Task("Walk", 20, "high", "exercise", "evening", False)

    # add task to pet
    pet.add_task(task)

    # verify task count increased
    assert len(pet.assigned_tasks) == 1