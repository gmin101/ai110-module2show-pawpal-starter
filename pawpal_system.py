"""PawPal+ system classes.

Owner owns Pets; each Pet owns its Tasks; the Scheduler pulls tasks
across ALL of an owner's pets and builds a prioritized plan.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields, replace
from datetime import date, datetime, time, timedelta


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
    # Calendar day this task is due. Left as None for tasks that only carry
    # a time-of-day; next_occurrence() then counts forward from today.
    due_date: date | None = None
    # Back-reference to the owning pet so tasks stay identifiable
    # after the Scheduler flattens them across pets.
    pet_name: str = ""

    # How far ahead each recurring frequency lands. A frequency absent from
    # this table (e.g. "once") is treated as non-repeating. Not annotated, so
    # the dataclass leaves it a plain class attribute rather than a field.
    _INTERVALS = {"daily": timedelta(days=1), "weekly": timedelta(days=7)}

    def mark_complete(self) -> None:
        """Mark this activity as done."""
        self.completed = True

    def end_time(self) -> time:
        """Clock time this task finishes: start time plus its duration.

        A task is assumed to stay within one day; a duration that would spill
        past midnight is clamped to 23:59 so same-day overlap checks stay
        well-behaved.

        Returns:
            The finish time of day (start time + duration_minutes).
        """
        finish = datetime.combine(date.min, self.time) + timedelta(
            minutes=self.duration_minutes
        )
        if finish.date() != date.min:
            return time(23, 59)
        return finish.time()

    def overlaps(self, other: Task) -> bool:
        """Report whether this task's time window collides with another's.

        Args:
            other: The task to compare this one against.

        Returns:
            True if the two share a start instant or their [start, end)
            windows overlap; False otherwise. A zero-duration task only
            conflicts with something starting at the exact same time.
        """
        if self.time == other.time:
            return True
        return self.time < other.end_time() and other.time < self.end_time()

    def next_occurrence(self, after: date | None = None) -> Task | None:
        """Build the next instance of a recurring task.

        The follow-up is a fresh, uncompleted copy with its due_date advanced
        by one interval (daily -> +1 day, weekly -> +7 days) via timedelta, so
        month/year rollovers are handled automatically. It also gets a new id
        (the original id plus the new date) so it can live alongside the
        completed original without colliding.

        Args:
            after: Date to count forward from. Defaults to this task's own
                due_date, or today if that is also unset.

        Returns:
            The next Task instance, or None if the frequency does not repeat.
        """
        interval = self._INTERVALS.get(self.frequency.lower())
        if interval is None:
            return None
        base = after or self.due_date or date.today()
        next_date = base + interval
        base_id = self.id.split("#")[0]
        return replace(
            self,
            id=f"{base_id}#{next_date.isoformat()}",
            completed=False,
            due_date=next_date,
        )

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

    def complete_task(self, task_id: str) -> Task | None:
        """Mark a task done and, if it recurs, queue its next occurrence.

        Args:
            task_id: Id of the task to complete.

        Returns:
            The newly created follow-up task (already attached to this pet),
            or None if the task does not repeat.

        Raises:
            KeyError: If no task on this pet has the given id.
        """
        task = self._find_task(task_id)
        task.mark_complete()
        follow_up = task.next_occurrence()
        if follow_up is not None:
            self.add_task(follow_up)
        return follow_up

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

    def filter_tasks(
        self,
        *,
        pet_name: str | None = None,
        completed: bool | None = None,
    ) -> list[Task]:
        """Return tasks across all pets, narrowed by pet name and/or status.

        Both filters are keyword-only and optional; leaving one as None means
        "don't filter on it". Passing neither returns every task.

        Args:
            pet_name: If given, keep only tasks belonging to this pet.
            completed: If given, keep only tasks with this completion status
                (False for still-to-do, True for done).

        Returns:
            The matching tasks, in collection order.

        Examples:
            filter_tasks(pet_name="Rex")                    # just Rex's tasks
            filter_tasks(completed=False)                   # still to do
            filter_tasks(pet_name="Rex", completed=False)   # both at once
        """
        tasks = self.collect_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name == pet_name]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks

    @staticmethod
    def sort_by_time(tasks: list[Task]) -> list[Task]:
        """Return the tasks ordered by time of day, earliest first.

        Task.time is a datetime.time, which is directly comparable, so the
        sort key hands each task's time straight to sorted().

        Args:
            tasks: The tasks to order.

        Returns:
            A new sorted list; the input list is left untouched.
        """
        return sorted(tasks, key=lambda t: t.time)

    def find_conflicts(
        self, tasks: list[Task] | None = None
    ) -> list[tuple[Task, Task]]:
        """Find pairs of tasks whose time windows collide, across all pets.

        Two tasks conflict when their times overlap (see Task.overlaps) -- the
        owner can't be in two places at once, whether the clash is within one
        pet's tasks or between different pets'. The tasks are sorted by start
        time first, so once a later task begins after the current one ends, no
        remaining task can overlap it and the inner scan stops early.

        Args:
            tasks: Tasks to check. Defaults to the owner's pending tasks; pass
                an explicit list to check a subset (e.g. a generated plan).

        Returns:
            A list of (earlier, later) task pairs, ordered by start time.
        """
        if tasks is None:
            tasks = self.pending_tasks()
        ordered = self.sort_by_time(tasks)

        conflicts: list[tuple[Task, Task]] = []
        for i, first in enumerate(ordered):
            for second in ordered[i + 1:]:
                if second.time > first.end_time():
                    break  # sorted by start: nothing later can overlap `first`
                if first.overlaps(second):
                    conflicts.append((first, second))
        return conflicts

    def conflict_warnings(self, tasks: list[Task] | None = None) -> list[str]:
        """Return human-readable warnings for time clashes without raising.

        A no-crash companion to find_conflicts: instead of raising when tasks
        collide, it returns one warning string per conflicting pair, so
        callers can print the result directly. Even the underlying scan is
        guarded, so malformed task data degrades to a single warning rather
        than taking the app down.

        Args:
            tasks: Tasks to check. Defaults to the owner's pending tasks.

        Returns:
            A list of warning strings, empty when the schedule is clear.
        """
        try:
            conflicts = self.find_conflicts(tasks)
        except Exception as err:  # never let a schedule check crash the caller
            return [f"Warning: could not check for conflicts ({err})"]

        return [
            f"Warning: {first.description} ({first.pet_name}, "
            f"{first.time:%H:%M}-{first.end_time():%H:%M}) overlaps "
            f"{second.description} ({second.pet_name}, "
            f"{second.time:%H:%M}-{second.end_time():%H:%M})"
            for first, second in conflicts
        ]

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
