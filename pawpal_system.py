"""PawPal+ system classes.

Skeleton generated from diagrams/uml_draft.mmd.
Owner owns Pets; each Pet owns its Tasks; the Scheduler pulls tasks
across ALL of an owner's pets and builds a prioritized plan.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time


@dataclass
class Task:
    id: str
    name: str
    description: str
    due_date: date
    due_time: time
    duration_minutes: int
    priority: int
    completed: bool = False

    def mark_complete(self) -> None:
        ...

    def edit(self, **changes) -> None:
        ...


@dataclass
class Walk(Task):
    location: str = ""


@dataclass
class Feeding(Task):
    food_type: str = ""
    portion: float = 0.0


@dataclass
class Medication(Task):
    medication_name: str = ""
    dosage: str = ""


@dataclass
class Enrichment(Task):
    activity_type: str = ""


@dataclass
class Grooming(Task):
    groom_type: str = ""


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        ...

    def edit_task(self, task_id: str, **changes) -> None:
        ...

    def delete_task(self, task_id: str) -> None:
        ...

    def list_tasks(self) -> list[Task]:
        ...


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        ...

    def remove_pet(self, pet_name: str) -> None:
        ...

    def list_pets(self) -> list[Pet]:
        ...

    def set_availability(self, minutes: int) -> None:
        ...

    def set_preferences(self, prefs: list[str]) -> None:
        ...


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def collect_tasks(self) -> list[Task]:
        ...

    def pending_tasks(self) -> list[Task]:
        ...

    def score_task(self, task: Task, preferences: list[str]) -> float:
        ...

    def generate_plan(self, available_minutes: int, preferences: list[str]) -> list[Task]:
        ...

    def explain(self, plan: list[Task]) -> str:
        ...
