"""PawPal+ demo script.

Builds a small owner/pet/task setup and prints today's schedule to the
terminal, using the scheduling logic from pawpal_system.py.
"""

from datetime import time

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner(
        name="Grace",
        available_minutes=90,
        preferences=["walk", "meds"],
    )

    # --- Pets ----------------------------------------------------------
    rex = Pet(name="Rex", species="dog", breed="Labrador", age=3)
    bella = Pet(name="Bella", species="cat", breed="Tabby", age=5)
    owner.add_pet(rex)
    owner.add_pet(bella)

    # --- Tasks (different times of day) --------------------------------
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
            id="t4",
            description="grooming",
            time=time(11, 0),
            frequency="weekly",
            duration_minutes=40,
            priority=2,
        )
    )

    # --- Today's Schedule ----------------------------------------------
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    print("Today's Schedule") 
    print(scheduler.explain(plan))


if __name__ == "__main__":
    main()
