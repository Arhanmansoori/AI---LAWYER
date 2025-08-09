import requests
import json

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key securely
API_KEY = os.getenv("GEMINI_API_KEY")
# Gemini 2.5 Flash model endpoint URL
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

def get_legal_consequences(scenario: str) -> str:
    prompt = f"""
You are an expert AI lawyer and judge strictly familiar with the Indian legal system. For the supplied legal scenario, analyze the case ONLY according to relevant Indian laws and return ONLY a JSON object specifying the legal consequences as follows:

JSON format:
{{
  "punishment": {{
    "type": one of ("death_penalty", "life_imprisonment", "jail", "fine", "compensation", "probation", "community_service", "none"),
    "details": {{
      "jail_years": (integer or null),
      "fine_amount": (number or null),
      "compensation_required": (true/false),
      "compensation_amount": (number or null)
    }}
  }},
  "severity": one of ("severe", "moderate", "mild"),
  "additional_notes": (optional, brief)
}}

Instructions:
- STRICTLY apply only Indian law when determining punishment and details. Do not consider or refer to legal systems from any other country or source.
- Set the correct "type" based on Indian law (for example: "death_penalty" instead of setting any death_penalty: true/false flag).
- If "punishment.type" is "death_penalty" or "life_imprisonment", set "jail_years" to null or omit it.
- "compensation_amount": For "mild" and "moderate" severity crimes, provide an appropriate amount. For "severe" crimes (like murder, rape, terrorism), set compensation_amount to null or 0.
- Only include relevant fields in the JSON object per the context. DO NOT include unused fields or explanations.
- DO NOT add any additional text or markdown, ONLY output the JSON object.

Scenario: {scenario}
"""
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY
    }
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    response = requests.post(GEMINI_ENDPOINT, headers=headers, json=data)
    try:
        result = response.json()
        text_response = result["candidates"][0]["content"]["parts"][0]["text"].strip()
        # Fix: properly check and strip markdown backticks
        if text_response.startswith("```"):
            text_response = text_response.strip("```").strip()
        parsed_json = json.loads(text_response)
        return json.dumps(parsed_json, indent=2)
    except (KeyError, json.JSONDecodeError) as e:
        return f"Error parsing response: {e}\nResponse text:\n{text_response}"
    except Exception as e:
        return f"Unexpected error: {e}\nFull API response:\n{response.text}"

if __name__ == "__main__":
    test_scenario = (
        "A boy less than 18 years old was convicted of intentional murder with clear evidence and no prior criminal record."
    )
    print(get_legal_consequences(test_scenario))
    
