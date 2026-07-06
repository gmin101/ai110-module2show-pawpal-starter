# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Today's Schedule
Planned 4 task(s) using 85 of 90 available minutes for Grace.

Scheduled:
  07:30 - morning meds (Bella, 5 min, priority 5, score 10)
  08:00 - morning walk (Rex, 30 min, priority 3, score 8)
  09:00 - breakfast feeding (Rex, 10 min, priority 4, score 4)
  11:00 - grooming (Bella, 40 min, priority 2, score 2)
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
tests\test_pawpal.py .....                                                            [100%]

==================================== 5 passed in 0.55s =====================================
```

Based on my test results, I have a confidence level of 5 stars in the system's reliability.

## Features

The scheduling logic in `pawpal_system.py` implements the following algorithms:

- **Sorting by time** — orders tasks chronologically by time of day (`Scheduler.sort_by_time`).
- **Priority + preference scoring** — ranks each task by its priority, with a bonus when its description matches one of the owner's care preferences (`Scheduler.score_task`).
- **Greedy time-budget planning** — packs the highest-scoring tasks into the owner's available minutes, recording anything that doesn't fit as "skipped" (`Scheduler.generate_plan`).
- **Overlap detection** — computes each task's end time and checks half-open `[start, end)` windows so back-to-back tasks don't count as clashing (`Task.end_time`, `Task.overlaps`).
- **Conflict warnings** — finds every pair of overlapping tasks across all pets and returns human-readable warnings without crashing on bad data (`Scheduler.find_conflicts`, `Scheduler.conflict_warnings`).
- **Filtering** — narrows tasks by pet and/or completion status (`Scheduler.filter_tasks`).
- **Daily & weekly recurrence** — completing a recurring task automatically queues its next occurrence one interval ahead, handling month/year rollovers (`Task.next_occurrence`, `Pet.complete_task`).
- **Plan explanation** — produces a readable justification of what was scheduled, when, and why, plus what was skipped (`Scheduler.explain`).

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | Scheduler.sort_by_time() | e.g., by priority, duration |
| Filtering | Scheduler.filter_tasks() | e.g., skip tasks if time runs out |
| Conflict handling | Scheduler.find_conflicts() | e.g., overlapping time slots |
| Recurring tasks | Task.next_occurrence() | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

1. Set the owner to Jordan and the pet to Mochi (a dog).
2. Add a task: Morning meds, 5 min, high priority, 07:30, daily.
3. Add a task: Morning walk, 30 min, medium priority, 08:00, daily.
4. Add a task: Grooming, 40 min, low priority, 11:00, weekly.
5. Set available minutes to 90 and preferences to `walk, meds`.
6. Click Generate schedule and read today's plan.

```
