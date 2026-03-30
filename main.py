from pawpal_system import Owner, Pet, Task, Scheduler

owner = Owner("Arav", "arav@email.com", 180)

dog = Pet("Buddy", "Dog", 3, [], [])
cat = Pet("Luna", "Cat", 2, [], [])

owner.add_pet(dog)
owner.add_pet(cat)

task1 = Task("Morning Walk", 30, "high", "exercise", "morning", False)
task2 = Task("Feed Cat", 10, "medium", "feeding", "afternoon", False)
task3 = Task("Play Time", 20, "low", "play", "evening", False)

dog.add_task(task1)
cat.add_task(task2)
dog.add_task(task3)

scheduler = Scheduler(owner, dog)

schedule = scheduler.generate_schedule()

print("Today's Schedule:\n")

for task in schedule:
    print(f"{task.time_of_day} - {task.title} ({task.duration_minutes} minutes)")