import os
import json

from openai import OpenAI
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_challenge_with_ai(difficulty: str) -> Dict[str, Any]:
    system_prompt = """
You are a coding challenge generator.

You MUST return ONLY a valid JSON object.
DO NOT include markdown.
DO NOT include explanations outside JSON.
DO NOT include code blocks.

The JSON schema MUST be exactly:

{
  "title": "string",
  "options": ["string", "string", "string", "string"],
  "correct_answer_id": number,
  "explanation": "string"
}

Rules:
- options MUST have exactly 4 items
- correct_answer_id MUST be 0, 1, 2, or 3
- Only ONE option is correct
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Generate a {difficulty} difficulty coding challenge."
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )

        content = response.choices[0].message.content.strip()
        print("===== RAW AI CONTENT =====")
        print(content)

        challenge_data = json.loads(content)

        # strict validation
        if not isinstance(challenge_data.get("options"), list) or len(challenge_data["options"]) != 4:
            raise ValueError("Options must be a list of exactly 4 items")

        if challenge_data.get("correct_answer_id") not in [0, 1, 2, 3]:
            raise ValueError("correct_answer_id must be between 0 and 3")

        return challenge_data

    except Exception as e:
        print("⚠ AI FAILED, USING FALLBACK:", e)
        return {
            "title": "Basic Python List Operation",
            "options": [
                "my_list.append(5)",
                "my_list.add(5)",
                "my_list.push(5)",
                "my_list.insert(5)",
            ],
            "correct_answer_id": 0,
            "explanation": "In Python, append() adds an element to the end of a list."
        }
