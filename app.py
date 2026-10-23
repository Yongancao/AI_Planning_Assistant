import time
from copy import deepcopy
from datetime import time as clock_time
from task_inputs import read_task_rows

import streamlit as st

from example_problem import problem as example_problem
from checker import check_plan, format_time
from llm_planner import generate_plan


st.set_page_config(
    page_title="AI Planning Assistant",
    layout="wide",
)

st.title("AI Planning Assistant")
st.write(
    "Generate a schedule, check its constraints, "
    "and revise it using symbolic feedback."
)

def clear_results():
    """Remove results when the requirements change."""
    st.session_state.attempts = []
    st.session_state.run_error = None


problem = deepcopy(example_problem)

st.subheader("Your available hours")
st.caption("Choose a start and end time within the same day.")

left, right = st.columns(2)

with left:
    start_time = st.time_input(
        "Available from",
        value=clock_time(13, 0),
        key="available_from",
        on_change=clear_results,
    )

with right:
    end_time = st.time_input(
        "Available until",
        value=clock_time(18, 0),
        key="available_until",
        on_change=clear_results,
    )

if start_time is None or end_time is None:
    st.warning("Select both a start and an end time.")
    st.stop()

problem["available_start"] = start_time.hour * 60 + start_time.minute
problem["available_end"] = end_time.hour * 60 + end_time.minute

if problem["available_end"] <= problem["available_start"]:
    st.error("The end time must be later than the start time.")
    st.stop()

st.subheader("Task requirements")
st.caption(
    "Edit cells directly. Add or delete rows using the table controls. "
    "Deadlines use 24-hour HH:MM format; leave blank for no deadline. "
    "In 'Must follow', enter exact task names separated by commas."
)

task_rows = []

for task in example_problem["tasks"]:
    deadline = task.get("deadline")

    task_rows.append({
        "Task": task["id"],
        "Required minutes": task["duration_minutes"],
        "Deadline": (
            format_time(deadline) if deadline is not None else ""
        ),
        "Must follow": ", ".join(task.get("depends_on", [])),
    })

edited_rows = st.data_editor(
    task_rows,
    hide_index=True,
    num_rows="dynamic",
    key="task_editor",
    on_change=clear_results,
    column_config={
        "Task": st.column_config.TextColumn(
            "Task",
            help="Use a unique name for each task.",
        ),
        "Required minutes": st.column_config.NumberColumn(
            "Required minutes",
            min_value=1,
            max_value=1440,
            step=1,
            format="%d",
        ),
        "Deadline": st.column_config.TextColumn(
            "Deadline",
            help="Example: 16:00. Leave blank for no deadline.",
        ),
        "Must follow": st.column_config.TextColumn(
            "Must follow",
            help="Example: groceries, review_notes",
        ),
    },
)

tasks, input_errors = read_task_rows(edited_rows)

if input_errors:
    for error in input_errors:
        st.error(error)
    st.stop()

problem["tasks"] = tasks

st.write(
    f"Available hours: "
    f"{format_time(problem['available_start'])} - "
    f"{format_time(problem['available_end'])}"
)

max_revisions = st.selectbox(
    "Maximum revisions after the initial plan",
    options=[0, 1, 2],
    index=2,
)

if "attempts" not in st.session_state:
    st.session_state.attempts = []

if "run_error" not in st.session_state:
    st.session_state.run_error = None

if st.button("Generate and check plan", type="primary"):
    st.session_state.attempts = []
    st.session_state.run_error = None

    previous_plan = None
    feedback = None

    for attempt in range(max_revisions + 1):
        label = (
            "Initial plan"
            if attempt == 0
            else f"Revision {attempt}"
        )

        try:
            with st.spinner(f"{label}: waiting for Gemini..."):
                started = time.perf_counter()

                plan = generate_plan(
                    problem,
                    previous_plan=previous_plan,
                    feedback=feedback,
                )

                elapsed = time.perf_counter() - started

        except Exception as error:
            # Keep raw exception details out of the browser.
            st.session_state.run_error = (
                f"{label} could not be generated "
                f"({type(error).__name__}). "
                "Check your connection, API configuration, and quota."
            )
            break

        result = check_plan(problem, plan)

        st.session_state.attempts.append({
            "label": label,
            "plan": plan,
            "result": result,
            "seconds": elapsed,
        })

        if result["valid"]:
            break

        previous_plan = plan
        feedback = result["errors"]


if st.session_state.run_error:
    st.error(st.session_state.run_error)

attempts = st.session_state.attempts

if attempts:
    st.subheader("Results")

    final_result = attempts[-1]["result"]

    if final_result["valid"]:
        st.success("A plan passed all implemented checks.")
    elif not st.session_state.run_error:
        st.warning(
            "The attempt limit was reached without a passing plan. "
            "This does not prove the requirements are impossible."
        )

    for attempt in attempts:
        result = attempt["result"]
        status = "PASS" if result["valid"] else "FAIL"

        with st.expander(
            f"{attempt['label']} | {status} | "
            f"{attempt['seconds']:.1f} seconds",
            expanded=True,
        ):
            if result["status"] != "invalid_input":
                schedule_rows = [
                    {
                        "Task": action["task_id"],
                        "Start": format_time(action["start"]),
                        "End": format_time(action["end"]),
                        "Minutes": action["end"] - action["start"],
                    }
                    for action in sorted(
                        attempt["plan"],
                        key=lambda action: action["start"],
                    )
                ]

                st.dataframe(schedule_rows, hide_index=True)

            if result["valid"]:
                st.success("All implemented constraints satisfied.")
            else:
                for error in result["errors"]:
                    st.error(f"{error['type']}: {error['message']}")

            st.caption("Raw candidate plan")
            st.json(attempt["plan"])