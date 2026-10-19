def validate_plan_structure(plan):
    """Check that a candidate plan has the expected data structure."""
    errors = []

    if not isinstance(plan, list):
        return [{
            "type": "invalid_plan",
            "message": "The plan must be a list of task entries.",
        }]

    for index, action in enumerate(plan):
        label = f"Entry {index + 1}"

        if not isinstance(action, dict):
            errors.append({
                "type": "invalid_entry",
                "message": f"{label} must be a dictionary.",
            })
            continue

        required_fields = ("task_id", "start", "end")

        for field in required_fields:
            if field not in action:
                errors.append({
                    "type": "missing_field",
                    "message": f"{label} is missing '{field}'.",
                })

        if "task_id" in action:
            task_id = action["task_id"]

            if not isinstance(task_id, str) or not task_id.strip():
                errors.append({
                    "type": "invalid_task_id",
                    "message": f"{label}: 'task_id' must be nonempty text.",
                })

        for field in ("start", "end"):
            if field in action and type(action[field]) is not int:
                errors.append({
                    "type": "invalid_time_type",
                    "message": (
                        f"{label}: '{field}' must be an integer "
                        "representing minutes after midnight."
                    ),
                })

    return errors