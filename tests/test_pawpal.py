"""Tests for core PawPal+ behaviors."""

import sys
from datetime import date, time
from pathlib import Path

# Make pawpal_system.py (in the repo root) importable when tests run.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pawpal_system import Owner, Pet, Scheduler, Task  # noqa: E402


def make_task(task_id: str = "t1") -> Task:
    return Task(
        id=task_id,
        description="morning walk",
        time=time(8, 0),
        frequency="daily",
        duration_minutes=30,
        priority=3,
    )


def make_scheduler(*tasks: Task) -> Scheduler:
    """Owner with one pet carrying the given tasks, wrapped in a Scheduler."""
    pet = Pet(name="Rex", species="dog", breed="Labrador", age=3)
    for task in tasks:
        pet.add_task(task)
    owner = Owner(name="Jordan", available_minutes=240)
    owner.add_pet(pet)
    return Scheduler(owner)


def test_mark_complete_changes_status():
    """mark_complete() flips a task from incomplete to complete."""
    task = make_task()
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet increases that pet's task count by one."""
    pet = Pet(name="Rex", species="dog", breed="Labrador", age=3)
    assert len(pet.tasks) == 0

    pet.add_task(make_task())

    assert len(pet.tasks) == 1


def test_sort_by_time_returns_chronological_order():
    """sort_by_time() orders tasks by time of day, earliest first."""
    noon = Task(id="noon", description="lunch", time=time(12, 0), frequency="daily")
    morning = Task(id="am", description="walk", time=time(8, 0), frequency="daily")
    evening = Task(id="pm", description="dinner", time=time(18, 0), frequency="daily")

    ordered = Scheduler.sort_by_time([noon, evening, morning])

    assert [t.id for t in ordered] == ["am", "noon", "pm"]


def test_complete_daily_task_creates_next_days_occurrence():
    """Completing a daily task queues a fresh copy due the following day."""
    pet = Pet(name="Rex", species="dog", breed="Labrador", age=3)
    task = make_task()
    task.due_date = date(2026, 7, 6)  # fixed date keeps the test deterministic
    pet.add_task(task)

    follow_up = pet.complete_task("t1")

    assert follow_up is not None
    assert follow_up.due_date == date(2026, 7, 7)
    assert follow_up.completed is False
    # Original stays completed; the new occurrence lives alongside it.
    assert task.completed is True
    assert follow_up in pet.tasks


def test_find_conflicts_flags_tasks_at_the_same_time():
    """Two tasks scheduled at the same time are reported as a conflict."""
    walk = Task(id="walk", description="walk", time=time(8, 0), frequency="daily")
    feed = Task(id="feed", description="feed", time=time(8, 0), frequency="daily")
    scheduler = make_scheduler(walk, feed)

    conflicts = scheduler.find_conflicts()

    assert len(conflicts) == 1
    assert {t.id for t in conflicts[0]} == {"walk", "feed"}
