from validation import validate_plan_structure

def format_time(minutes):
    """Convert minutes after midnight into HH:MM."""
    hours, remaining_minutes = divmod(minutes, 60)
    return f"{hours:02d}:{remaining_minutes:02d}"


def check_overlaps(plan):
    """Return a list of overlapping task pairs."""
    errors = []

    for i in range(len(plan)):
        for j in range(i + 1, len(plan)):
            first = plan[i]
            second = plan[j]

            overlap_start = max(first["start"], second["start"])
            overlap_end = min(first["end"], second["end"])

            if overlap_start < overlap_end:
                errors.append({
                    "type": "overlap",
                    "tasks": [first["task_id"], second["task_id"]],
                    "start": overlap_start,
                    "end": overlap_end,
                    "minutes": overlap_end - overlap_start,
                })

    return errors

def check_task_coverage(problem, plan):
    """Check for missing, duplicate, and unknown tasks."""
    errors = []

    required_ids = {task["id"] for task in problem["tasks"]}

    # Count how many times each task appears in the plan.
    counts = {}
    for action in plan:
        task_id = action["task_id"]
        counts[task_id] = counts.get(task_id, 0) + 1

    # Check whether every required task appears.
    for task_id in sorted(required_ids):
        if task_id not in counts:
            errors.append({
                "type": "missing_task",
                "task_id": task_id,
                "message": f"Required task '{task_id}' is missing.",
            })

    # Check for unknown tasks and repeated tasks.
    for task_id, count in counts.items():
        if task_id not in required_ids:
            errors.append({
                "type": "unknown_task",
                "task_id": task_id,
                "message": f"Task '{task_id}' is not in the requirements.",
            })

        if count > 1:
            errors.append({
                "type": "duplicate_task",
                "task_id": task_id,
                "message": (
                    f"Task '{task_id}' appears {count} times; "
                    "expected exactly once."
                ),
            })

    return errors

def check_task_times(problem, plan):
    """Check time boundaries and minimum task durations."""
    errors = []

    tasks_by_id = {
        task["id"]: task
        for task in problem["tasks"]
    }

    for action in plan:
        task_id = action["task_id"]
        start = action["start"]
        end = action["end"]

        # This version supports a single day: 0 through 1440 minutes.
        if not (0 <= start < end <= 24 * 60):
            errors.append({
                "type": "invalid_time_range",
                "task_id": task_id,
                "message": (
                    f"Task '{task_id}' must have "
                    "0 <= start < end <= 1440."
                ),
            })
            continue

        # Unknown tasks are reported by the coverage checker.
        if task_id not in tasks_by_id:
            continue

        required = tasks_by_id[task_id]["duration_minutes"]
        scheduled = end - start

        if scheduled < required:
            errors.append({
                "type": "insufficient_duration",
                "task_id": task_id,
                "message": (
                    f"Task '{task_id}' needs {required} minutes, "
                    f"but only {scheduled} minutes are scheduled."
                ),
            })

    return errors

def check_availability_and_deadlines(problem, plan):
    """Check available hours and each task's deadline."""
    errors = []

    available_start = problem["available_start"]
    available_end = problem["available_end"]

    tasks_by_id = {
        task["id"]: task
        for task in problem["tasks"]
    }

    for action in plan:
        task_id = action["task_id"]
        start = action["start"]
        end = action["end"]

        # Invalid ranges are reported by check_task_times.
        if not (0 <= start < end <= 24 * 60):
            continue

        if start < available_start or end > available_end:
            errors.append({
                "type": "outside_availability",
                "task_id": task_id,
                "message": (
                    f"Task '{task_id}' is scheduled outside "
                    f"available hours "
                    f"{format_time(available_start)}-"
                    f"{format_time(available_end)}."
                ),
            })

        # Unknown tasks are reported by the coverage checker.
        if task_id not in tasks_by_id:
            continue

        deadline = tasks_by_id[task_id].get("deadline")

        if deadline is not None and end > deadline:
            errors.append({
                "type": "missed_deadline",
                "task_id": task_id,
                "message": (
                    f"Task '{task_id}' ends at {format_time(end)}, "
                    f"after its deadline of {format_time(deadline)}."
                ),
            })

    return errors

def check_dependencies(problem, plan):
    """Check that prerequisites finish before dependent tasks start."""
    errors = []

    # Keep every occurrence so duplicates are not silently overwritten.
    entries_by_id = {}
    for action in plan:
        task_id = action["task_id"]
        entries_by_id.setdefault(task_id, []).append(action)

    required_ids = {task["id"] for task in problem["tasks"]}

    for task in problem["tasks"]:
        task_id = task["id"]
        task_entries = entries_by_id.get(task_id, [])

        # Coverage checking handles missing or duplicated tasks.
        if len(task_entries) != 1:
            continue

        current = task_entries[0]

        for prerequisite_id in task.get("depends_on", []):
            # Input validation will handle invalid dependency references.
            if prerequisite_id not in required_ids:
                continue

            prerequisite_entries = entries_by_id.get(prerequisite_id, [])

            if len(prerequisite_entries) != 1:
                continue

            prerequisite = prerequisite_entries[0]

            # Time checking handles invalid ranges.
            if not (
                0 <= current["start"] < current["end"] <= 1440
                and 0 <= prerequisite["start"] < prerequisite["end"] <= 1440
            ):
                continue

            if prerequisite["end"] > current["start"]:
                errors.append({
                    "type": "dependency_violation",
                    "task_id": task_id,
                    "prerequisite_id": prerequisite_id,
                    "message": (
                        f"Task '{task_id}' starts at "
                        f"{format_time(current['start'])}, "
                        f"but prerequisite '{prerequisite_id}' "
                        f"does not finish until "
                        f"{format_time(prerequisite['end'])}."
                    ),
                })

    return errors

def check_plan(problem, plan):
    """Check a candidate plan against trusted problem requirements."""

    # Stop before other checks if the plan's structure is invalid.
    structure_errors = validate_plan_structure(plan)

    if structure_errors:
        return {
            "valid": False,
            "status": "invalid_input",
            "errors": structure_errors,
        }

    errors = []

    errors.extend(check_task_coverage(problem, plan))
    errors.extend(check_task_times(problem, plan))

    # Only compare intervals with valid time ranges.
    valid_intervals = [
        action
        for action in plan
        if 0 <= action["start"] < action["end"] <= 1440
    ]

    overlap_errors = check_overlaps(valid_intervals)

    # Give overlaps a message, just like the other errors.
    for error in overlap_errors:
        first, second = error["tasks"]

        error["message"] = (
            f"Tasks '{first}' and '{second}' overlap "
            f"from {format_time(error['start'])} "
            f"to {format_time(error['end'])} "
            f"({error['minutes']} minutes)."
        )

    errors.extend(overlap_errors)
    errors.extend(check_availability_and_deadlines(problem, plan))
    errors.extend(check_dependencies(problem, plan))

    return {
        "valid": len(errors) == 0,
        "status": "passed" if not errors else "violations_found",
        "errors": errors,
    }