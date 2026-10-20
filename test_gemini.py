import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


def main():
    env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(env_path)

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL")

    if not api_key or not model:
        print("Missing GEMINI_API_KEY or GEMINI_MODEL in .env.")
        return

    client = genai.Client(api_key=api_key)

    print(f"Connecting to {model}...")

    response = client.interactions.create(
        model=model,
        input="Reply with one short sentence confirming you can respond.",
    )

    print("\nGemini response:")
    print(response.output_text)


if __name__ == "__main__":
    main()