import time

import streamlit as st

from example_problem import problem
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

st.subheader("Task requirements")
st.caption("This prototype uses the example problem saved in your project.")

st.write(
    f"Available hours: "
    f"{format_time(problem['available_start'])} - "
    f"{format_time(problem['available_end'])}"
)

task_rows = []
for task in problem["tasks"]:
    deadline = task.get("deadline")

    task_rows.append({
        "Task": task["id"],
        "Required minutes": task["duration_minutes"],
        "Deadline": (
            format_time(deadline) if deadline is not None else "None"
        ),
        "Must follow": ", ".join(task.get("depends_on", [])) or "None",
    })

st.dataframe(task_rows, hide_index=True)

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