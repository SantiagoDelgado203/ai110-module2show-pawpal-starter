import os
from datetime import date, time
from pathlib import Path

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

DATA_FILE = Path(os.environ.get("PAWPAL_DATA_FILE", Path(__file__).parent / "data.json"))
PRIORITY_BADGES = {"high": "🔴 high", "medium": "🟡 medium", "low": "🟢 low"}

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

# --- Application "memory" -------------------------------------------------
# Streamlit reruns this script on every interaction, so the Owner lives in
# st.session_state. On the first run of a session it's loaded from data.json.
if "owner" not in st.session_state:
    st.session_state.owner = Owner.load_from_json(DATA_FILE) or Owner("Jordan", 120)

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)


def save() -> None:
    """Persist the current owner, pets, and tasks to data.json."""
    owner.save_to_json(DATA_FILE)


def flash(kind: str, message: str) -> None:
    """Queue a message to show after the next rerun."""
    st.session_state.flash = (kind, message)


def task_rows(pairs) -> list[dict]:
    """Turn (pet, task) pairs into display rows for st.dataframe."""
    return [
        {
            "Done": "✅" if t.completed else "⬜",
            "Time": t.time,
            "Pet": p.name,
            "Task": f"{t.emoji()} {t.description}",
            "Minutes": t.duration_minutes,
            "Priority": PRIORITY_BADGES[t.priority],
            "Repeats": t.frequency,
            "Date": t.due_date.strftime("%a %b %d"),
        }
        for p, t in pairs
    ]


# --- Sidebar: owner + pets ------------------------------------------------
with st.sidebar:
    st.header("👤 Owner")
    new_name = st.text_input("Owner name", value=owner.name)
    new_minutes = int(st.number_input("Minutes available per day", 0, 1440,
                                      owner.available_minutes, step=15))
    if (new_name, new_minutes) != (owner.name, owner.available_minutes):
        owner.name, owner.available_minutes = new_name, new_minutes
        save()

    st.header("🐶 Add a pet")
    with st.form("add_pet_form", clear_on_submit=True):
        pet_name = st.text_input("Pet name", placeholder="Mochi")
        c1, c2 = st.columns(2)
        species = c1.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])
        age = c2.number_input("Age", min_value=0, max_value=40, value=1)
        if st.form_submit_button("Add pet", width="stretch"):
            if not pet_name.strip():
                st.error("Please enter a pet name.")
            else:
                try:
                    owner.add_pet(Pet(pet_name.strip(), species, int(age)))
                    save()
                    flash("success", f"Added {pet_name.strip()}! 🎉")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

    if owner.pets:
        st.header("🏠 Your pets")
        for p in owner.pets:
            st.markdown(f"**{p.name}** · {p.species}, {p.age} yr · "
                        f"{len(p.get_pending_tasks())} pending")

    st.divider()
    if st.button("🗑️ Reset all data", width="stretch"):
        st.session_state.owner = Owner("Jordan", 120)
        DATA_FILE.unlink(missing_ok=True)
        flash("info", "All data cleared.")
        st.rerun()
    st.caption(f"Data is saved automatically to `{DATA_FILE.name}`.")

# --- Main area ------------------------------------------------------------
st.title("🐾 PawPal+")
st.caption("A smart planner for feedings, walks, medications, and appointments.")

if "flash" in st.session_state:
    kind, message = st.session_state.pop("flash")
    getattr(st, kind)(message)

if not owner.pets:
    st.info("👈 Start by adding a pet in the sidebar.")
    st.stop()

day = st.date_input("📅 Day", value=date.today())

tab_schedule, tab_add, tab_plan = st.tabs(["📋 Schedule", "➕ Add task", "🧠 Smart plan"])

# --- Schedule tab ---------------------------------------------------------
with tab_schedule:
    conflicts = scheduler.detect_conflicts(day)
    if conflicts:
        st.warning(
            f"**⚠️ {len(conflicts)} scheduling conflict(s).** You can't be in two places at "
            "once. Consider moving one of these tasks:\n\n"
            + "\n".join(f"- {c.removeprefix('Conflict ')}" for c in conflicts)
        )

    c1, c2, c3 = st.columns([2, 1, 1])
    pet_filter = c1.multiselect("Pets", [p.name for p in owner.pets],
                                placeholder="All pets")
    status = c2.radio("Status", ["All", "Pending", "Done"], horizontal=True)
    sort_mode = c3.radio("Sort by", ["Time", "Priority"], horizontal=True)

    completed = {"All": None, "Pending": False, "Done": True}[status]
    pairs = scheduler.filter_tasks(completed=completed, day=day)
    if pet_filter:
        pairs = [(p, t) for p, t in pairs if p.name in pet_filter]
    pairs = scheduler.sort_by_time(pairs) if sort_mode == "Time" else scheduler.sort_by_priority(pairs)

    if pairs:
        st.dataframe(task_rows(pairs), hide_index=True, width="stretch")
    else:
        st.info("No tasks match for this day.")

    day_tasks = scheduler.get_todays_schedule(day)
    total = sum(t.duration_minutes for _, t in day_tasks)
    done = sum(t.duration_minutes for _, t in day_tasks if t.completed)
    m1, m2, m3 = st.columns(3)
    m1.metric("Tasks", len(day_tasks))
    m2.metric("Minutes planned", total, delta=f"{owner.available_minutes - total} vs. available",
              delta_color="normal" if total <= owner.available_minutes else "inverse")
    m3.metric("Minutes done", done)

    pending = [(p, t) for p, t in day_tasks if not t.completed]
    if pending:
        st.subheader("Mark a task complete")
        cc1, cc2 = st.columns([3, 1])
        choice = cc1.selectbox(
            "Task", range(len(pending)), label_visibility="collapsed",
            format_func=lambda i: f"{pending[i][1].time} · {pending[i][0].name} · "
                                  f"{pending[i][1].emoji()} {pending[i][1].description}",
        )
        if cc2.button("✅ Complete", width="stretch"):
            pet, task = pending[choice]
            nxt = pet.complete_task(task, completed_on=max(day, date.today()))
            save()
            msg = f"Completed **{task.description}** for {pet.name}."
            if nxt:
                msg += f" Next {task.frequency} occurrence added for {nxt.due_date:%a %b %d}."
            flash("success", msg)
            st.rerun()

# --- Add task tab ---------------------------------------------------------
with tab_add:
    with st.form("add_task_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        target_pet = c1.selectbox("Pet", [p.name for p in owner.pets])
        task_desc = c1.text_input("Task", placeholder="Morning walk")
        task_date = c1.date_input("Date", value=day)
        task_time = c1.time_input("Time", value=time(8, 0), step=900)
        auto_slot = c1.checkbox("🔎 Use the next free slot instead of this time")
        duration = c2.number_input("Duration (minutes)", min_value=1, max_value=600, value=20)
        priority = c2.selectbox("Priority", ["high", "medium", "low"], index=1)
        frequency = c2.selectbox("Repeats", ["once", "daily", "weekly"], index=1)
        submitted = st.form_submit_button("Add task", type="primary")

    if submitted:
        if not task_desc.strip():
            st.error("Please enter a task description.")
        else:
            start = task_time.strftime("%H:%M")
            if auto_slot:
                start = scheduler.find_next_available_slot(int(duration), task_date)
            if start is None:
                st.error(f"No free {duration}-minute slot left on {task_date:%b %d}.")
            else:
                try:
                    task = Task(task_desc.strip(), start, int(duration), priority,
                                frequency, due_date=task_date)
                    owner.get_pet(target_pet).add_task(task)
                    save()
                    msg = f"Scheduled {task.emoji()} **{task.description}** for {target_pet} at {task.time}."
                    new_conflicts = [c for c in scheduler.detect_conflicts(task_date)
                                     if task.description in c]
                    flash("warning" if new_conflicts else "success",
                          msg + (" ⚠️ It overlaps another task. Check the Schedule tab."
                                 if new_conflicts else ""))
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

    st.caption(
        "💡 Next free slots on this day: "
        + ", ".join(f"{m} min → {scheduler.find_next_available_slot(m, day) or 'none'}"
                    for m in (15, 30, 60))
    )

# --- Smart plan tab -------------------------------------------------------
with tab_plan:
    st.markdown(
        f"Picks which **pending** tasks fit in your **{owner.available_minutes} available "
        "minutes**. Higher priority goes first, and earlier time breaks ties."
    )
    plan = scheduler.build_plan(day)
    if not plan:
        st.info("Nothing pending for this day. 🎉")
    else:
        skipped = [e for e in plan if not e.included]
        if skipped:
            st.warning(f"{len(skipped)} task(s) don't fit in today's time budget: "
                       + ", ".join(f"{e.pet.name}'s {e.task.description}" for e in skipped))
        else:
            st.success("Everything pending fits in your available time. ✅")
        st.dataframe(
            [{"": "✔️" if e.included else "✖️", "Time": e.task.time, "Pet": e.pet.name,
              "Task": f"{e.task.emoji()} {e.task.description}",
              "Priority": PRIORITY_BADGES[e.task.priority],
              "Minutes": e.task.duration_minutes, "Why": e.reason} for e in plan],
            hide_index=True, width="stretch",
        )
