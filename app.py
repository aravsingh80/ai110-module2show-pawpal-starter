from pawpal_system import Owner, Pet, Task, Scheduler
import streamlit as st

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Step 1: Import is already done above.
#
# Step 2: Initialize persistent objects in session_state once per session.
#         Streamlit re-runs this file top-to-bottom on every interaction,
#         so we guard with "if key not in st.session_state" to avoid
#         re-creating objects and losing data.
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = None  # created when the user sets their name

if "pet" not in st.session_state:
    st.session_state.pet = None  # created when the user sets pet info

if "scheduler" not in st.session_state:
    st.session_state.scheduler = None  # created once owner + pet exist

# ---------------------------------------------------------------------------
# Owner & Pet setup
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
    # Step 3: Wire the form submission to class constructors and store in
    #         session_state so the objects survive the next re-run.
    owner = Owner(name=owner_name, email="", available_minutes_per_day=int(available_minutes))
    pet = Pet(name=pet_name, species=species, age=0)
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.pet = pet
    st.session_state.scheduler = Scheduler(owner=owner, pet=pet)
    st.success(f"Saved! Owner: {owner.name} | Pet: {pet.name} ({pet.species})")

# ---------------------------------------------------------------------------
# Task entry — only shown once owner & pet are set up
# ---------------------------------------------------------------------------

st.divider()
st.subheader("Tasks")

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

    if st.button("Add task"):
        # Step 3: Call Task() and Scheduler.add_task() — data goes into the
        #         real objects stored in session_state, not a plain dict list.
        new_task = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
        )
        st.session_state.scheduler.add_task(new_task)
        st.success(f"Added: {new_task.title}")

    tasks = st.session_state.pet.assigned_tasks
    if tasks:
        st.write("Current tasks:")
        st.table(
            [
                {
                    "title": t.title,
                    "duration_minutes": t.duration_minutes,
                    "priority": t.priority,
                }
                for t in tasks
            ]
        )
    else:
        st.info("No tasks yet. Add one above.")

# ---------------------------------------------------------------------------
# Schedule generation
# ---------------------------------------------------------------------------

st.divider()
st.subheader("Build Schedule")

if st.session_state.scheduler is None:
    st.info("Save owner & pet info above to enable scheduling.")
elif not st.session_state.pet.assigned_tasks:
    st.info("Add at least one task before generating a schedule.")
else:
    if st.button("Generate schedule"):
        # Step 3: Call the real Scheduler method and display its output.
        scheduled = st.session_state.scheduler.generate_schedule()
        explanation = st.session_state.scheduler.explain_plan()
        st.success("Schedule generated!")
        st.text(explanation)
        if len(scheduled) < len(st.session_state.pet.assigned_tasks):
            skipped = len(st.session_state.pet.assigned_tasks) - len(scheduled)
            st.warning(
                f"{skipped} task(s) skipped — not enough time in the day."
            )
