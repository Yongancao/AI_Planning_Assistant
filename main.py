from example_problem import problem
from llm_planner import generate_plan
from checker import check_plan, format_time


def display_result(plan, result):
    """Display a candidate plan and the checker's findings."""
    if result["status"] == "invalid_input":
        print("\nThe plan has an invalid structure.")
    else:
        print("\nCandidate plan:")

        for action in plan:
            start = format_time(action["start"])
            end = format_time(action["end"])
            print(f"- {action['task_id']}: {start}-{end}")

    if result["valid"]:
        print("\nPASS: All implemented constraints are satisfied.")
    else:
        print(f"\nFAIL: Found {len(result['errors'])} issue(s).")

        for error in result["errors"]:
            print(f"- [{error['type']}] {error['message']}")


def main():
    print("AI Planning Assistant")

    max_revisions = 2
    previous_plan = None
    feedback = None

    for attempt in range(max_revisions + 1):
        if attempt == 0:
            print("\nGenerating initial plan...")
        else:
            print(f"\nRevision {attempt} of {max_revisions}...")

        try:
            plan = generate_plan(
                problem,
                previous_plan=previous_plan,
                feedback=feedback,
            )
        except ValueError as error:
            print(f"\nGeneration failed: {error}")
            return

        result = check_plan(problem, plan)
        display_result(plan, result)

        if result["valid"]:
            print(f"\nFinished after {attempt} revision(s).")
            return

        previous_plan = plan
        feedback = result["errors"]

    print("\nRevision limit reached. No valid plan was found.")
    print("This does not prove that the requirements are impossible.")


if __name__ == "__main__":
    main()