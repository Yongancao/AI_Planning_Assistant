from graphlib import TopologicalSorter, CycleError


def read_task_rows(rows):
    """Convert editable table rows into task requirements."""
    tasks = []
    errors = []
    seen_ids = set()

    if not rows:
        return [], ["Add at least one task."]

    for number, row in enumerate(rows, start=1):
        label = f"Row {number}"

        task_id = row.get("Task")
        if not isinstance(task_id, str) or not task_id.strip():
            errors.append(f"{label}: enter a task name.")
            continue

        task_id = task_id.strip()

        if "," in task_id:
            errors.append(f"{label}: task names cannot contain commas.")
            continue

        if task_id in seen_ids:
            errors.append(f"{label}: task name '{task_id}' is repeated.")
            continue

        seen_ids.add(task_id)

        duration = row.get("Required minutes")

        # Table editors can return whole numbers as floats.
        if (
            type(duration) not in (int, float)
            or not 1 <= duration <= 1440
            or int(duration) != duration
        ):
            errors.append(
                f"{label}: duration must be a whole number from 1 to 1440."
            )
            continue

        deadline_text = row.get("Deadline")
        deadline = None

        if deadline_text not in (None, ""):
            try:
                hours, minutes = deadline_text.strip().split(":")

                if (
                    len(hours) != 2
                    or len(minutes) != 2
                    or not hours.isdigit()
                    or not minutes.isdigit()
                ):
                    raise ValueError

                hours, minutes = int(hours), int(minutes)

                if not (
                    (0 <= hours <= 23 and 0 <= minutes <= 59)
                    or (hours == 24 and minutes == 0)
                ):
                    raise ValueError

                deadline = hours * 60 + minutes

            except (ValueError, AttributeError):
                errors.append(
                    f"{label}: use HH:MM for the deadline, "
                    "such as 16:00, or leave it blank."
                )
                continue

        dependency_text = row.get("Must follow") or ""

        if not isinstance(dependency_text, str):
            errors.append(f"{label}: prerequisites must be task names.")
            continue

        dependencies = [
            name.strip()
            for name in dependency_text.split(",")
            if name.strip()
        ]

        tasks.append({
            "id": task_id,
            "duration_minutes": int(duration),
            "deadline": deadline,
            "depends_on": list(dict.fromkeys(dependencies)),
        })

    if errors:
        return [], errors

    task_ids = {task["id"] for task in tasks}

    for task in tasks:
        for prerequisite in task["depends_on"]:
            if prerequisite not in task_ids:
                errors.append(
                    f"'{task['id']}' refers to unknown task '{prerequisite}'."
                )
            elif prerequisite == task["id"]:
                errors.append(
                    f"'{task['id']}' cannot depend on itself."
                )

    if not errors:
        graph = {
            task["id"]: task["depends_on"]
            for task in tasks
        }

        try:
            tuple(TopologicalSorter(graph).static_order())
        except CycleError:
            errors.append(
                "Dependencies contain a cycle. "
                "Tasks cannot require each other to finish first."
            )

    return tasks, errors