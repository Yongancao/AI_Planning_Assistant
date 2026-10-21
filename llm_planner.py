import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
import time


def generate_plan(problem, previous_plan=None, feedback=None):
    """Ask Gemini to generate a schedule from the requirements."""
    env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(env_path)

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL")

    if not api_key or not model:
        raise ValueError("Missing GEMINI_API_KEY or GEMINI_MODEL in .env.")

    client = genai.Client(api_key=api_key)

    prompt = """
Create a single-day schedule satisfying these requirements:

- Include every required task exactly once.
- Do not include unknown tasks.
- Each task must occupy one continuous block.
- All times must be integer minutes after midnight, from 0 to 1440.
- Each task's end must be greater than its start.
- Allocate at least duration_minutes to each task.
- Tasks cannot overlap.
- All tasks must fit within available_start and available_end.
- If a task has a deadline, finish it by that deadline.
- If a task has depends_on, all listed prerequisites must finish
  before or exactly when that task starts.
- Do not change the supplied requirements.

Return ONLY a JSON array, without Markdown fences or explanation.
Each entry must have exactly these fields:
{"task_id": "task_identifier", "start": 780, "end": 840}

Problem requirements:
"""
    print(f"Using model: {model}")
    request_text = prompt + json.dumps(problem, indent=2)

    if previous_plan is not None and feedback is not None:
        request_text += (
            "\n\nYour previous candidate plan:\n"
            + json.dumps(previous_plan, indent=2)
            + "\n\nErrors reported by the checker:\n"
            + json.dumps(feedback, indent=2)
            + "\n\nReturn a revised COMPLETE schedule that fixes these errors."
            + "\nKeep the original requirements unchanged."
            + "\nReturn only the JSON array."
        )
    request_start = time.perf_counter()

    response = client.interactions.create(
        model=model,
        input=request_text,
        generation_config={
            "thinking_level": "low",
        },
    )

    elapsed = time.perf_counter() - request_start
    print(f"Gemini API request took {elapsed:.1f} seconds.")

    text = response.output_text

    if not text or not text.strip():
        raise ValueError("Gemini returned no text.")

    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError(
            "Gemini returned text that was not valid JSON."
        ) from error