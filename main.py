from example_problem import problem, candidate_plan
from validation import validate_plan_structure
from checker import (
    check_overlaps,
    check_task_coverage,
    check_task_times,
    check_availability_and_deadlines,
    check_dependencies,
    format_time,
)


def main():
    print("AI Planning Assistant")

    structure_errors = validate_plan_structure(candidate_plan)

    if structure_errors:
        print("\nInput validation failed:")
        for error in structure_errors:
            print(f"- {error['message']}")
        return

    print("\nCandidate plan:")
    for action in candidate_plan:
        start = format_time(action["start"])
        end = format_time(action["end"])
        print(f"- {action['task_id']}: {start}-{end}")

    print("\nOverlap check:")
    overlap_errors = check_overlaps(candidate_plan)

    if overlap_errors:
        for error in overlap_errors:
            first, second = error["tasks"]
            print(
                f"- {first} and {second} overlap "
                f"from {format_time(error['start'])} "
                f"to {format_time(error['end'])} "
                f"({error['minutes']} minutes)."
            )
    else:
        print("No overlaps found.")

    checks = [
        ("Task coverage", check_task_coverage),
        ("Time and duration", check_task_times),
        ("Availability and deadlines", check_availability_and_deadlines),
        ("Dependencies", check_dependencies),
    ]

    for label, check_function in checks:
        print(f"\n{label} check:")
        errors = check_function(problem, candidate_plan)

        if errors:
            for error in errors:
                print(f"- {error['message']}")
        else:
            print("No violations found.")


if __name__ == "__main__":
    main()