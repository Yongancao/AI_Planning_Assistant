from example_problem import problem, candidate_plan
from checker import (
    check_overlaps,
    check_task_coverage,
    check_task_times,
    check_availability_and_deadlines,
    check_dependencies,
    format_time,
)


print("AI Planning Assistant")

print("\nCandidate plan:")
for action in candidate_plan:
    start = format_time(action["start"])
    end = format_time(action["end"])

    print(f"- {action['task_id']}: {start}-{end}")

errors = check_overlaps(candidate_plan)

print("\nOverlap check:")
if errors:
    for error in errors:
        first, second = error["tasks"]
        start = format_time(error["start"])
        end = format_time(error["end"])

        print(
            f"- {first} and {second} overlap "
            f"from {start} to {end} "
            f"({error['minutes']} minutes)."
        )
else:
    print("No overlaps found.")
    
coverage_errors = check_task_coverage(problem, candidate_plan)

print("\nTask coverage check:")
if coverage_errors:
    for error in coverage_errors:
        print(f"- {error['message']}")
else:
    print("All required tasks appear exactly once. No unknown tasks.")
    
time_errors = check_task_times(problem, candidate_plan)

print("\nTime and duration check:")
if time_errors:
    for error in time_errors:
        print(f"- {error['message']}")
else:
    print("All time ranges are valid and task durations are sufficient.")
    
    
constraint_errors = check_availability_and_deadlines(
    problem, candidate_plan
)

print("\nAvailability and deadline check:")
if constraint_errors:
    for error in constraint_errors:
        print(f"- {error['message']}")
else:
    print("All tasks fit available hours and meet their deadlines.")
    
dependency_errors = check_dependencies(problem, candidate_plan)

print("\nDependency check:")
if dependency_errors:
    for error in dependency_errors:
        print(f"- {error['message']}")
else:
    print("No dependency ordering violations found.")