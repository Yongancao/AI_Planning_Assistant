# All times are minutes after midnight.
# 13 * 60 = 1:00 PM; 18 * 60 = 6:00 PM.

problem = {
    "available_start": 13 * 60,
    "available_end": 18 * 60,
    "tasks": [
        {
            "id": "ml_homework",
            "duration_minutes": 120,
            "deadline": 18 * 60,
        },
        {
            "id": "groceries",
            "duration_minutes": 60,
            "deadline": 16 * 60,
        },
        {
            "id": "exercise",
            "duration_minutes": 60,
            "deadline": 18 * 60,
            "depends_on": ["groceries"],
        },
    ],
}

# A proposed schedule with an intentional overlap.
candidate_plan = [
    {
        "task_id": "ml_homework",
        "start": 13 * 60,
        "end": 15 * 60,
    },
    {
        "task_id": "groceries",
        "start": 15 * 60,
        "end": 16 * 60,
    },
    {
        "task_id": "exercise",
        "start": 16 * 60,
        "end": 17 * 60,
    },
]