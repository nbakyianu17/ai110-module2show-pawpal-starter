import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- Session state bootstrap ---
if "owner" not in st.session_state:
    st.session_state.owner = None

# ── Step 1: Owner setup ───────────────────────────────────────────────────────
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
    st.success(f"Owner saved: {owner_name} ({available_minutes} min available)")

# Everything below requires an owner to exist
if st.session_state.owner is None:
    st.info("Fill in your name and time above to get started.")
    st.stop()

owner: Owner = st.session_state.owner

st.divider()

# ── Step 2: Add a pet ─────────────────────────────────────────────────────────
st.subheader("Add a Pet")

with st.form("pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    add_pet = st.form_submit_button("Add pet")

if add_pet:
    new_pet = Pet(name=pet_name, species=species)
    owner.add_pet(new_pet)
    st.success(f"Added {pet_name} the {species}!")

if owner.pets:
    st.write("**Your pets:**")
    for pet in owner.pets:
        st.write(f"- {pet.name} ({pet.species})")
else:
    st.info("No pets added yet.")

st.divider()

# ── Step 3: Add a task to a pet ───────────────────────────────────────────────
st.subheader("Add a Task")

if not owner.pets:
    st.warning("Add a pet first before adding tasks.")
else:
    pet_names = [p.name for p in owner.pets]

    with st.form("task_form"):
        selected_pet_name = st.selectbox("Assign to pet", pet_names)
        task_title = st.text_input("Task title", value="Morning walk")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        add_task = st.form_submit_button("Add task")

    if add_task:
        target_pet = next(p for p in owner.pets if p.name == selected_pet_name)
        target_pet.add_task(Task(title=task_title, duration_minutes=int(duration), priority=priority))
        st.success(f"Added '{task_title}' to {selected_pet_name}.")

    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.write("**Current tasks:**")
        st.table([
            {"pet": p.name, "task": t.title, "duration (min)": t.duration_minutes, "priority": t.priority}
            for p in owner.pets
            for t in p.get_tasks()
        ])
    else:
        st.info("No tasks yet.")

st.divider()

# ── Step 4: Generate schedule ─────────────────────────────────────────────────
st.subheader("Generate Today's Schedule")

if st.button("Generate schedule"):
    if not owner.get_all_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        plan = Scheduler(owner).generate_plan()
        st.code(plan.explain(), language=None)
