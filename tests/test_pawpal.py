"""Tests for core PawPal+ behaviors."""

import sys
from datetime import time
from pathlib import Path

# Make pawpal_system.py (in the repo root) importable when tests run.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pawpal_system import Pet, Task  # noqa: E402


def make_task(task_id: str = "t1") -> Task:
    return Task(
        id=task_id,
        description="morning walk",
        time=time(8, 0),
        frequency="daily",
        duration_minutes=30,
        priority=3,
    )


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
