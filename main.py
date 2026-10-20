from example_problem import problem, candidate_plan
from checker import check_plan, format_time


def main():
    print("AI Planning Assistant")

    result = check_plan(problem, candidate_plan)

    if result["status"] == "invalid_input":
        print("\nCannot check plan: invalid input.")
    else:
        print("\nCandidate plan:")

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