from datetime import time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

# Map the UI's friendly priority labels onto the integer scores the
# Scheduler ranks with (higher = more important).
PRIORITY_LEVELS = {"low": 1, "medium": 3, "high": 5}

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5 = st.columns(2)
with col4:
    task_time = st.time_input("Time of day", value=time(8, 0))
with col5:
    frequency = st.selectbox("Frequency", ["daily", "weekly", "once"], index=0)

if st.button("Add task"):
    st.session_state.tasks.append(
        {
            "title": task_title,
            "duration_minutes": int(duration),
            "priority": priority,
            "time": task_time,
            "frequency": frequency,
        }
    )

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "Time": t["time"].strftime("%H:%M"),
                "Task": t["title"],
                "Duration (min)": t["duration_minutes"],
                "Priority": t["priority"],
                "Frequency": t["frequency"],
            }
            for t in st.session_state.tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Runs your Scheduler over the tasks above: ranks them, packs them into your available time, and flags time conflicts.")

available_minutes = st.number_input(
    "Available minutes today", min_value=0, max_value=1440, value=90
)
preferences_raw = st.text_input(
    "Care preferences (comma-separated)",
    value="walk, meds",
    help="Tasks whose description matches a preference get a scoring bonus.",
)


def build_scheduler() -> Scheduler:
    """Turn the UI's session-state tasks into a live Scheduler."""
    preferences = [p.strip() for p in preferences_raw.split(",") if p.strip()]
    owner = Owner(
        name=owner_name or "Owner",
        available_minutes=int(available_minutes),
        preferences=preferences,
    )
    pet = Pet(name=pet_name or "Pet", species=species, breed="", age=0)
    owner.add_pet(pet)
    for i, t in enumerate(st.session_state.tasks):
        pet.add_task(
            Task(
                id=f"task-{i}",
                description=t["title"],
                time=t["time"],
                frequency=t["frequency"],
                duration_minutes=t["duration_minutes"],
                priority=PRIORITY_LEVELS.get(t["priority"], 1),
            )
        )
    return Scheduler(owner)


if st.button("Generate schedule"):
    if not st.session_state.tasks:
        st.info("Add at least one task before generating a schedule.")
    else:
        scheduler = build_scheduler()

        # 1. Conflicts first, so the owner sees clashes up front.
        warnings = scheduler.conflict_warnings()
        if warnings:
            for warning in warnings:
                st.warning(warning)
        else:
            st.success("No time conflicts detected.")

        # 2. The generated plan (greedy pack into available time).
        plan = scheduler.generate_plan()
        used = sum(t.duration_minutes for t in plan)
        st.success(
            f"Planned {len(plan)} task(s) using {used} of "
            f"{int(available_minutes)} available minutes."
        )

        if plan:
            st.markdown("#### 📅 Today's Plan")
            st.table(
                [
                    {
                        "Time": t.time.strftime("%H:%M"),
                        "Task": t.description,
                        "Pet": t.pet_name,
                        "Duration (min)": t.duration_minutes,
                        "Priority": t.priority,
                        "Score": f"{scheduler.scores.get(t.id, 0):g}",
                    }
                    for t in plan
                ]
            )

        # 3. Anything that didn't fit the time budget.
        if scheduler.skipped:
            st.markdown("#### ⏱️ Skipped (not enough time)")
            st.table(
                [
                    {
                        "Task": t.description,
                        "Pet": t.pet_name,
                        "Needs (min)": t.duration_minutes,
                    }
                    for t in scheduler.skipped
                ]
            )

        # 4. All tasks in chronological order, via Scheduler.sort_by_time.
        st.markdown("#### 🕒 All Tasks (sorted by time)")
        st.table(
            [
                {
                    "Time": t.time.strftime("%H:%M"),
                    "Task": t.description,
                    "Duration (min)": t.duration_minutes,
                    "Priority": t.priority,
                    "Frequency": t.frequency,
                }
                for t in scheduler.sort_by_time(scheduler.collect_tasks())
            ]
        )

        # 5. The human-readable justification.
        with st.expander("Why this plan? (explanation)"):
            st.text(scheduler.explain(plan))
