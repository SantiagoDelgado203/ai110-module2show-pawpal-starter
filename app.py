from datetime import time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' daily care: feedings, walks, medications, and appointments.")

# --- Application "memory" -------------------------------------------------
# Streamlit reruns this script top-to-bottom on every interaction, so the
# Owner object lives in st.session_state and is only created once per session.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", available_minutes=120)

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

# --- Owner ----------------------------------------------------------------
st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with col2:
    owner.available_minutes = int(
        st.number_input(
            "Minutes available today", min_value=0, max_value=1440,
            value=owner.available_minutes, step=15,
        )
    )

st.divider()

# --- Add a pet ------------------------------------------------------------
st.subheader("Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        pet_name = st.text_input("Pet name", placeholder="Mochi")
    with c2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with c3:
        age = st.number_input("Age", min_value=0, max_value=40, value=1)
    if st.form_submit_button("Add pet"):
        if not pet_name.strip():
            st.error("Please enter a pet name.")
        else:
            try:
                owner.add_pet(Pet(pet_name.strip(), species, int(age)))
                st.success(f"Added {pet_name.strip()}!")
            except ValueError as e:
                st.error(str(e))

if owner.pets:
    st.table(
        [{"Name": p.name, "Species": p.species, "Age": p.age, "Tasks": p.task_count()}
         for p in owner.pets]
    )
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Schedule a task ------------------------------------------------------
st.subheader("Schedule a Task")
if not owner.pets:
    st.caption("Add a pet first to schedule tasks.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            target_pet = st.selectbox("Pet", [p.name for p in owner.pets])
            task_desc = st.text_input("Task", placeholder="Morning walk")
            task_time = st.time_input("Time", value=time(8, 0), step=900)
        with c2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
            frequency = st.selectbox("Frequency", ["once", "daily", "weekly"], index=1)
        if st.form_submit_button("Add task"):
            if not task_desc.strip():
                st.error("Please enter a task description.")
            else:
                try:
                    task = Task(
                        task_desc.strip(), task_time.strftime("%H:%M"),
                        int(duration), priority, frequency,
                    )
                    owner.get_pet(target_pet).add_task(task)
                    st.success(f"Scheduled '{task.description}' for {target_pet} at {task.time}.")
                except ValueError as e:
                    st.error(str(e))

st.divider()

# --- Today's schedule -----------------------------------------------------
st.subheader("Today's Schedule")
schedule = scheduler.get_todays_schedule()
if not schedule:
    st.info("No tasks scheduled yet.")
else:
    for i, (pet, task) in enumerate(schedule):
        label = (f"**{task.time}** — {pet.name}: {task.description} "
                 f"({task.duration_minutes} min, {task.priority}, {task.frequency})")
        done = st.checkbox(label, value=task.completed, key=f"done_{i}_{pet.name}_{task.description}")
        if done != task.completed:
            task.mark_complete() if done else task.mark_incomplete()
            st.rerun()

    total = sum(t.duration_minutes for _, t in schedule)
    remaining = sum(t.duration_minutes for _, t in schedule if not t.completed)
    st.caption(f"{len(schedule)} tasks · {total} min total · {remaining} min remaining · "
               f"{owner.available_minutes} min available")
    if total > owner.available_minutes:
        st.warning("Today's tasks take more time than you have available.")
