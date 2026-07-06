"""PawPal+ demo script.

Builds a small owner/pet/task setup and prints today's schedule to the
terminal, using the scheduling logic from pawpal_system.py.
"""

from datetime import date, time

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner(
        name="Grace",
        available_minutes=90,
        preferences=["walk", "meds"],
    )

    rex = Pet(name="Rex", species="dog", breed="Labrador", age=3)
    bella = Pet(name="Bella", species="cat", breed="Tabby", age=5)
    owner.add_pet(rex)
    owner.add_pet(bella)

    rex.add_task(
        Task(
            id="t2",
            description="morning walk",
            time=time(8, 0),
            frequency="daily",
            duration_minutes=30,
            priority=3,
        )
    )
    bella.add_task(
        Task(
            id="t4",
            description="grooming",
            time=time(11, 0),
            frequency="weekly",
            duration_minutes=40,
            priority=2,
        )
    )
    
    rex.add_task(
        Task(
            id="t3",
            description="breakfast feeding",
            time=time(9, 0),
            frequency="daily",
            duration_minutes=10,
            priority=4,
        )
    )
    bella.add_task(
        Task(
            id="t1",
            description="morning meds",
            time=time(7, 30),
            frequency="daily",
            duration_minutes=5,
            priority=5,
        )
    )

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    print("Today's Schedule") 
    print(scheduler.explain(plan))


def test_sort_by_time_returns_chronological_order() -> None:
    """Sorting Correctness: tasks come back in chronological order."""
    noon = Task(id="noon", description="lunch", time=time(12, 0), frequency="daily")
    morning = Task(id="am", description="walk", time=time(8, 0), frequency="daily")
    evening = Task(id="pm", description="dinner", time=time(18, 0), frequency="daily")

    ordered = Scheduler.sort_by_time([noon, evening, morning])

    assert [t.id for t in ordered] == ["am", "noon", "pm"]


def test_complete_daily_task_creates_next_days_occurrence() -> None:
    """Recurrence Logic: completing a daily task queues a copy due tomorrow."""
    pet = Pet(name="Rex", species="dog", breed="Labrador", age=3)
    task = Task(
        id="t1",
        description="morning walk",
        time=time(8, 0),
        frequency="daily",
        duration_minutes=30,
        priority=3,
        due_date=date(2026, 7, 6),  # fixed date keeps the test deterministic
    )
    pet.add_task(task)

    follow_up = pet.complete_task("t1")

    assert follow_up is not None
    assert follow_up.due_date == date(2026, 7, 7)
    assert follow_up.completed is False
    assert task.completed is True
    assert follow_up in pet.tasks


def test_find_conflicts_flags_tasks_at_the_same_time() -> None:
    """Conflict Detection: two tasks at the same time are flagged."""
    walk = Task(id="walk", description="walk", time=time(8, 0), frequency="daily")
    feed = Task(id="feed", description="feed", time=time(8, 0), frequency="daily")
    pet = Pet(name="Rex", species="dog", breed="Labrador", age=3)
    pet.add_task(walk)
    pet.add_task(feed)
    owner = Owner(name="Jordan", available_minutes=240)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    conflicts = scheduler.find_conflicts()

    assert len(conflicts) == 1
    assert {t.id for t in conflicts[0]} == {"walk", "feed"}


def run_tests() -> None:
    """Run the drafted test functions and report the result."""
    tests = [
        test_sort_by_time_returns_chronological_order,
        test_complete_daily_task_creates_next_days_occurrence,
        test_find_conflicts_flags_tasks_at_the_same_time,
    ]
    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
    print(f"All {len(tests)} tests passed.")


if __name__ == "__main__":
    main()
    print()
    run_tests()
