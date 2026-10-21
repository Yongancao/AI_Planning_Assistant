from example_problem import problem
from llm_planner import generate_plan
from checker import check_plan, format_time


def main():
    print("AI Planning Assistant")
    print("\nAsking Gemini to generate a schedule...")

    try:
        candidate_plan = generate_plan(problem)
    except ValueError as error:
        print(f"\nGeneration failed: {error}")
        return

    result = check_plan(problem, candidate_plan)

    if result["status"] == "invalid_input":
        print("\nGemini returned a plan with an invalid structure.")
    else:
        print("\nLLM-generated plan:")

        for action in candidate_plan:
            start = format_time(action["start"])
            end = format_time(action["end"])

            print(f"- {action['task_id']}: {start}-{end}")

        print("\nChecker result:")

        if result["valid"]:
            print("PASS: All implemented constraints are satisfied.")
        else:
            print(f"FAIL: Found {len(result['errors'])} violation(s).")

    for error in result["errors"]:
        print(f"- [{error['type']}] {error['message']}")


if __name__ == "__main__":
    main()