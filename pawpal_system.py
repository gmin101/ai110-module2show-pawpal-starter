"""PawPal+ system classes.

Owner owns Pets; each Pet owns its Tasks; the Scheduler pulls tasks
across ALL of an owner's pets and builds a prioritized plan.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from datetime import time


@dataclass
class Task:
    """A single pet-care activity (e.g. a morning walk)."""

    id: str  # caller-supplied identifier used for edit/delete lookups
    description: str
    time: time  # time of day the activity should happen
    frequency: str  # how often it repeats, e.g. "daily", "weekly"
    completed: bool = False
    # Fields the Scheduler needs to rank and fit tasks:
    duration_minutes: int = 0
    priority: int = 0
    # Back-reference to the owning pet so tasks stay identifiable
    # after the Scheduler flattens them across pets.
    pet_name: str = ""

    def mark_complete(self) -> None:
        """Mark this activity as done."""
        self.completed = True

    def edit(self, **changes) -> None:
        """Update one or more fields in place.

        Rejects unknown field names so typos (e.g. prioirty=5) fail loudly
        instead of silently creating a junk attribute.
        """
        valid = {f.name for f in fields(self)}
        for key, value in changes.items():
            if key not in valid:
                raise AttributeError(f"Task has no field {key!r}")
            setattr(self, key, value)


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def _find_task(self, task_id: str) -> Task:
        """Return the task with this id, or raise KeyError."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise KeyError(f"{self.name} has no task with id {task_id!r}")

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet, stamping the back-reference."""
        if any(t.id == task.id for t in self.tasks):
            raise ValueError(f"duplicate task id {task.id!r} for {self.name}")
        task.pet_name = self.name
        self.tasks.append(task)

    def edit_task(self, task_id: str, **changes) -> None:
        """Edit an existing task by id."""
        self._find_task(task_id).edit(**changes)

    def delete_task(self, task_id: str) -> None:
        """Remove a task by id."""
        task = self._find_task(task_id)
        self.tasks.remove(task)

    def list_tasks(self) -> list[Task]:
        """Return a shallow copy of this pet's tasks."""
        return list(self.tasks)


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def _find_pet(self, pet_name: str) -> Pet:
        """Return the pet with this name, or raise KeyError."""
        for pet in self.pets:
            if pet.name == pet_name:
                return pet
        raise KeyError(f"no pet named {pet_name!r}")

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner, rejecting duplicate names."""
        if any(p.name == pet.name for p in self.pets):
            raise ValueError(f"duplicate pet name {pet.name!r}")
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove the pet with this name."""
        self.pets.remove(self._find_pet(pet_name))

    def list_pets(self) -> list[Pet]:
        """Return a shallow copy of this owner's pets."""
        return list(self.pets)

    def set_availability(self, minutes: int) -> None:
        """Set how many minutes the owner has available today."""
        if minutes < 0:
            raise ValueError("available minutes cannot be negative")
        self.available_minutes = minutes

    def set_preferences(self, prefs: list[str]) -> None:
        """Replace the owner's care preferences."""
        self.preferences = list(prefs)


class Scheduler:
    """Builds a daily plan from tasks across all of an owner's pets.

    Scheduling strategy: score every pending task (priority + preference
    match), then greedily pack the highest-scoring tasks into the owner's
    available time. Tasks that don't fit are recorded as skipped so the
    plan can be explained.
    """

    PREFERENCE_BONUS = 5.0

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler bound to an owner and their pets."""
        self.owner = owner
        # Populated by generate_plan(); read by explain() to justify the plan.
        self.skipped: list[Task] = []
        self.scores: dict[str, float] = {}  # task id -> score

    def collect_tasks(self) -> list[Task]:
        """Every task across every pet, flattened into one list."""
        tasks: list[Task] = []
        for pet in self.owner.pets:
            tasks.extend(pet.tasks)
        return tasks

    def pending_tasks(self) -> list[Task]:
        """Tasks that still need doing (not yet completed)."""
        return [t for t in self.collect_tasks() if not t.completed]

    def score_task(self, task: Task) -> float:
        """Rank a task: higher priority wins, preference matches add a bonus."""
        score = float(task.priority)
        description = task.description.lower()
        for pref in self.owner.preferences:
            if pref.lower() in description:
                score += self.PREFERENCE_BONUS
        return score

    def generate_plan(self) -> list[Task]:
        """Greedily pack the highest-scoring pending tasks into the
        owner's available time. Records scores and skipped tasks as state.
        """
        self.scores = {}
        self.skipped = []

        pending = self.pending_tasks()
        for task in pending:
            self.scores[task.id] = self.score_task(task)

        # Best first: highest score, then shorter tasks, then earlier time.
        ordered = sorted(
            pending,
            key=lambda t: (-self.scores[t.id], t.duration_minutes, t.time),
        )

        plan: list[Task] = []
        remaining = self.owner.available_minutes
        for task in ordered:
            if task.duration_minutes <= remaining:
                plan.append(task)
                remaining -= task.duration_minutes
            else:
                self.skipped.append(task)

        # Present the plan in chronological order for the day.
        plan.sort(key=lambda t: t.time)
        return plan

    def explain(self, plan: list[Task]) -> str:
        """Human-readable justification for the generated plan."""
        lines: list[str] = []
        used = sum(t.duration_minutes for t in plan)
        available = self.owner.available_minutes

        lines.append(
            f"Planned {len(plan)} task(s) using {used} of {available} "
            f"available minutes for {self.owner.name}."
        )

        if plan:
            lines.append("")
            lines.append("Scheduled:")
            for task in plan:
                score = self.scores.get(task.id, 0.0)
                lines.append(
                    f"  {task.time.strftime('%H:%M')} - {task.description} "
                    f"({task.pet_name}, {task.duration_minutes} min, "
                    f"priority {task.priority}, score {score:g})"
                )

        if self.skipped:
            lines.append("")
            lines.append("Skipped (not enough time):")
            for task in self.skipped:
                lines.append(
                    f"  {task.description} ({task.pet_name}, "
                    f"needs {task.duration_minutes} min)"
                )

        return "\n".join(lines)
