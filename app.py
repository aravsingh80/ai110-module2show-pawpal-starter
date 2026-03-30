from pawpal_system import Owner, Pet, Task, Scheduler
import streamlit as st

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state — persistent objects across Streamlit re-runs
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = None
if "pet" not in st.session_state:
    st.session_state.pet = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None
if "last_schedule" not in st.session_state:
    st.session_state.last_schedule = []

# ---------------------------------------------------------------------------
# Section 1 — Owner & Pet setup
# ---------------------------------------------------------------------------

st.subheader("Owner & Pet Info")

col_a, col_b = st.columns(2)
with col_a:
    owner_name = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input(
        "Available minutes today", min_value=10, max_value=480, value=120
    )
with col_b:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Save owner & pet"):
    owner = Owner(name=owner_name, email="", available_minutes_per_day=int(available_minutes))
    pet = Pet(name=pet_name, species=species, age=0)
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.pet = pet
    st.session_state.scheduler = Scheduler(owner=owner, pet=pet)
    st.session_state.last_schedule = []
    st.success(f"Saved! Owner: **{owner.name}** | Pet: **{pet.name}** ({pet.species}) | Budget: {int(available_minutes)} min")

# ---------------------------------------------------------------------------
# Section 2 — Task entry
# ---------------------------------------------------------------------------

st.divider()
st.subheader("Add Tasks")

if st.session_state.pet is None:
    st.info("Save owner & pet info above before adding tasks.")
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    col4, col5, col6 = st.columns(3)
    with col4:
        start_time = st.text_input("Start time (HH:MM)", value="", placeholder="e.g. 08:00")
    with col5:
        frequency = st.selectbox("Frequency", ["one-off", "daily", "weekly"])
    with col6:
        task_pet_name = st.text_input("Pet name (for task)", value=st.session_state.pet.name)

    if st.button("Add task"):
        new_task = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            start_time=start_time.strip(),
            frequency="" if frequency == "one-off" else frequency,
            pet_name=task_pet_name,
        )
        st.session_state.scheduler.add_task(new_task)
        st.success(f"Added: **{new_task.title}** ({new_task.priority} priority, {new_task.duration_minutes} min)")

# ---------------------------------------------------------------------------
# Section 3 — Task list with sorting, filtering, conflict warnings
# ---------------------------------------------------------------------------

st.divider()
st.subheader("Task List")

if st.session_state.pet is None or not st.session_state.pet.assigned_tasks:
    st.info("No tasks yet. Add one above.")
else:
    sched = st.session_state.scheduler
    pet   = st.session_state.pet

    # --- Filter controls ---
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        status_filter = st.radio("Show", ["All", "Pending", "Completed"], horizontal=True)
    with col_f2:
        sort_mode = st.radio("Sort by", ["Priority", "Start time"], horizontal=True)

    tasks = pet.assigned_tasks
    if status_filter == "Pending":
        tasks = sched.filter_by_status(tasks, completed=False)
    elif status_filter == "Completed":
        tasks = sched.filter_by_status(tasks, completed=True)

    if sort_mode == "Start time":
        tasks = sched.sort_by_time(tasks)
    else:
        tasks = sorted(tasks, key=lambda t: t.get_priority_score(), reverse=True)

    if not tasks:
        st.info("No tasks match the current filter.")
    else:
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        st.table(
            [
                {
                    "": priority_emoji.get(t.priority, "⚪"),
                    "Title": t.title,
                    "Priority": t.priority,
                    "Duration (min)": t.duration_minutes,
                    "Start time": t.start_time or "—",
                    "Frequency": t.frequency or "one-off",
                    "Done": "✅" if t.is_completed else "⬜",
                }
                for t in tasks
            ]
        )

    # --- Conflict warnings ---
    conflicts = sched.detect_conflicts(pet.assigned_tasks)
    if conflicts:
        st.warning("**⚠️ Schedule conflicts detected** — two or more tasks overlap in time:")
        for w in conflicts:
            st.markdown(f"- {w}")
        st.caption("Tip: adjust start times or durations to resolve conflicts before generating your schedule.")

# ---------------------------------------------------------------------------
# Section 4 — Generate & display schedule
# ---------------------------------------------------------------------------

st.divider()
st.subheader("Daily Schedule")

if st.session_state.scheduler is None:
    st.info("Save owner & pet info above to enable scheduling.")
elif not st.session_state.pet.assigned_tasks:
    st.info("Add at least one task before generating a schedule.")
else:
    if st.button("Generate schedule"):
        scheduled = st.session_state.scheduler.generate_schedule()
        st.session_state.last_schedule = scheduled

    if st.session_state.last_schedule:
        sched = st.session_state.scheduler
        pet   = st.session_state.pet

        # Summary metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Tasks scheduled", len(sched.scheduled_tasks))
        m2.metric("Minutes used", sched.total_minutes_used)
        m3.metric("Minutes remaining", sched.get_remaining_time())

        # Sorted chronological view of scheduled tasks
        sorted_schedule = sched.sort_by_time(sched.scheduled_tasks)
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        st.table(
            [
                {
                    "": priority_emoji.get(t.priority, "⚪"),
                    "Task": t.title,
                    "Start": t.start_time or "flexible",
                    "Duration (min)": t.duration_minutes,
                    "Priority": t.priority,
                    "Recurring": t.frequency or "—",
                }
                for t in sorted_schedule
            ]
        )

        # Skipped tasks
        all_tasks = pet.assigned_tasks
        skipped = [t for t in all_tasks if t not in sched.scheduled_tasks and not t.is_completed]
        if skipped:
            st.warning(
                f"**{len(skipped)} task(s) could not fit in your {sched.owner.available_minutes_per_day}-minute budget:**"
            )
            for t in skipped:
                st.markdown(f"- {t.title} ({t.duration_minutes} min, {t.priority} priority)")
            st.caption("Consider increasing your available minutes or removing lower-priority tasks.")
        else:
            st.success("All tasks fit within your daily budget!")

        # Conflict check on the scheduled subset
        schedule_conflicts = sched.detect_conflicts(sched.scheduled_tasks)
        if schedule_conflicts:
            st.warning("**⚠️ Conflicts in your schedule:**")
            for w in schedule_conflicts:
                st.markdown(f"- {w}")
