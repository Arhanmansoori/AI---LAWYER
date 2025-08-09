import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()


API_KEY = os.getenv("GEMINI_API_KEY")

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

        # Strip markdown backticks if present
        if text_response.startswith("```"):
            text_response = text_response.strip("```").strip()

        # Strip leading 'json ' prefix if present
        if text_response.lower().startswith("json "):
            text_response = text_response[5:].strip()

        parsed_json = json.loads(text_response)
        return json.dumps(parsed_json, indent=2)
    except (KeyError, json.JSONDecodeError) as e:
        # Sometimes text_response may be empty or cause issues, so safeguard here
        snippet = text_response if 'text_response' in locals() else "[No response text]"
        return f"Error parsing response: {e}\nResponse text:\n{snippet}"
    except Exception as e:
        return f"Unexpected error: {e}\nFull API response:\n{response.text}"


def main():
    st.set_page_config(page_title="Indian Legal Consequences AI", page_icon="⚖️")
    st.title("Indian Legal Consequences AI Analyzer ⚖️")
    st.write(
        """
        Enter a legal scenario involving Indian law below.  
        The AI will provide the legal consequences strictly following Indian legal standards.
        """
    )

    scenario_input = st.text_area(
        "Enter legal scenario",
        height=200,
        placeholder="Describe the legal scenario here..."
    )

    if st.button("Analyze Scenario"):
        if not scenario_input.strip():
            st.error("Please enter a legal scenario to analyze.")
            return

        with st.spinner("Analyzing scenario and fetching legal consequences..."):
            result = get_legal_consequences(scenario_input)

        # Attempt to nicely display JSON, or show raw text if error
        try:
            parsed = json.loads(result)
            st.subheader("Legal Consequences (JSON Output):")
            st.json(parsed)
        except Exception:
            st.subheader("Response:")
            st.text(result)


if __name__ == "__main__":
    main()
