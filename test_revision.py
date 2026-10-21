from example_problem import problem
from checker import check_plan
from llm_planner import generate_plan
from main import display_result


def main():
    print("Testing revision with a deliberately invalid plan")

    bad_plan = [
        {"task_id": "ml_homework", "start": 780, "end": 900},
        {"task_id": "groceries", "start": 900, "end": 960},
        {"task_id": "exercise", "start": 930, "end": 990},
    ]

    initial_result = check_plan(problem, bad_plan)
    display_result(bad_plan, initial_result)

    if initial_result["valid"]:
        print("Test setup error: the starting plan should fail.")
        return

    print("\nSending the failed plan and checker feedback to Gemini...")

    revised_plan = generate_plan(
        problem,
        previous_plan=bad_plan,
        feedback=initial_result["errors"],
    )

    revised_result = check_plan(problem, revised_plan)

    print("\nRevision result:")
    display_result(revised_plan, revised_result)


if __name__ == "__main__":
    main()