import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# ── Session state bootstrap ───────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = None

# ── Owner setup ───────────────────────────────────────────────────────────────
st.subheader("Owner Setup")

with st.form("owner_form"):
    owner_name = st.text_input("Your name", value="Jordan")
    available_minutes = st.number_input(
        "Time available today (minutes)", min_value=10, max_value=480, value=60
    )
    submitted = st.form_submit_button("Save owner")

if submitted:
    if st.session_state.owner is None:
        st.session_state.owner = Owner(name=owner_name, available_minutes=available_minutes)
    else:
        st.session_state.owner.name = owner_name
        st.session_state.owner.available_minutes = available_minutes
    st.success(f"Saved: {owner_name} — {available_minutes} min available today")

if st.session_state.owner is None:
    st.info("Fill in your name and time above to get started.")
    st.stop()

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

st.divider()

# ── Add a pet ─────────────────────────────────────────────────────────────────
st.subheader("Add a Pet")

with st.form("pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    add_pet = st.form_submit_button("Add pet")

if add_pet:
    owner.add_pet(Pet(name=pet_name, species=species))
    st.success(f"Added {pet_name} the {species}!")

if owner.pets:
    st.write("**Your pets:** " + "  |  ".join(f"{p.name} ({p.species})" for p in owner.pets))
else:
    st.info("No pets added yet.")

st.divider()

# ── Add a task ────────────────────────────────────────────────────────────────
st.subheader("Add a Task")

if not owner.pets:
    st.warning("Add a pet first before adding tasks.")
else:
    pet_names = [p.name for p in owner.pets]

    with st.form("task_form"):
        col1, col2 = st.columns(2)
        with col1:
            selected_pet_name = st.selectbox("Assign to pet", pet_names)
            task_title = st.text_input("Task title", value="Morning walk")
            start_time = st.text_input("Start time (HH:MM, optional)", value="")
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
            frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])
        add_task = st.form_submit_button("Add task")

    if add_task:
        target_pet = next(p for p in owner.pets if p.name == selected_pet_name)
        target_pet.add_task(Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            frequency=frequency,
            start_time=start_time.strip() or None,
        ))
        st.success(f"Added '{task_title}' to {selected_pet_name}.")

    # Task table sorted by time
    all_tasks = owner.get_all_tasks()
    if all_tasks:
        sorted_tasks = scheduler.sort_by_time(all_tasks)
        st.write("**Current tasks** (sorted by start time):")
        st.table([
            {
                "pet":           next(p.name for p in owner.pets if t in p.get_tasks()),
                "task":          t.title,
                "start time":    t.start_time or "—",
                "duration (min)":t.duration_minutes,
                "priority":      t.priority,
                "frequency":     t.frequency,
                "done":          "✓" if t.completed else "",
            }
            for t in sorted_tasks
        ])

        # Conflict warnings — surface these prominently
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.warning("**Scheduling conflicts detected:**")
            for warning in conflicts:
                st.warning(f"⚠ {warning}")
    else:
        st.info("No tasks yet.")

st.divider()

# ── Generate schedule ─────────────────────────────────────────────────────────
st.subheader("Today's Schedule")

if st.button("Generate schedule"):
    if not owner.get_all_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        plan = scheduler.generate_plan()

        if plan.scheduled_tasks:
            st.success(f"Scheduled {len(plan.scheduled_tasks)} task(s) — {plan.total_minutes_used} min used")
            st.table([
                {
                    "task":          t.title,
                    "start time":    t.start_time or "—",
                    "duration (min)":t.duration_minutes,
                    "priority":      t.priority,
                }
                for t in plan.scheduled_tasks
            ])
        else:
            st.warning("No tasks could be scheduled within your available time.")

        if plan.skipped_tasks:
            with st.expander(f"Skipped tasks ({len(plan.skipped_tasks)})"):
                for task in plan.skipped_tasks:
                    reason = plan.skipped_reasons.get(task.title, "unknown reason")
                    st.warning(f"**{task.title}** — {reason}")
