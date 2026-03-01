from google import genai
from dotenv import load_dotenv
import os
import json
import requests
import re

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client()


def analyze_api(api_name: str) -> dict:
    """
    Calls the API first, captures its response, then evaluates using Gemini.
    """
    api_doc = api_name

    # ---------- INTERNAL HELPER FUNCTION ----------
    def call_api(api_url: str) -> str:
        """Call the API and return raw response as string."""
        try:
            res = requests.get(api_url, timeout=10)

            # Try to return JSON nicely formatted if possible
            try:
                return json.dumps(res.json(), indent=2)
            except Exception:
                return res.text

        except requests.exceptions.RequestException as e:
            return f"ERROR: {str(e)}"

    # ------------------------------------------------

    # STEP 1: Call API automatically
    api_response = call_api(api_name)

    # STEP 2: Build Gemini prompt
    prompt = f"""
You are a strict API quality evaluator.

EVALUATION CRITERIA:

If the response contains an error:
- Score MUST be 0
- Comment must:
    • Clearly state what the error is
    • Provide ONE short possible fix

If the response is valid, provide a list of six numbers:

1. Overall score out of 10
2. Structural clarity score out of 100
3. Completeness score out of 100
4. Documentation alignment score out of 100
5. Naming clarity score out of 100
6. AI-friendliness score out of 100

COMMENT REQUIREMENTS:
- One concise evaluation
- If valid, include ONE specific improvement suggestion

INPUTS:

API_DOCUMENTATION:
{api_doc}

API_RESPONSE:
{api_response}

OUTPUT FORMAT (STRICT):
Return ONLY JSON:
- "score": list of six numbers as described above. always return a list of 6 numbers, never return just 0 even for errors
- "comment": string containing the error if any or anything that findings, remediations and
  friction_points do not cover.
- "status_code": integer indicating the overall health of the API request 
- "findings":  [],          # List of issues
- "remediation": "",     # Step-by-step fix
- "friction_points": "",   # Why AI struggles with it
• 200 – OK 
• 400 – Faulty input 
• 401 – Unauthorized (private API without key) 
• 422 – Dead/unresponsive links 
• 503 – Service Unavailable (e.g. Gemini is down)

an example of a valid output is: 
{{
  "score": [...],
  "comment": "...",
  "status_code": 200,
  "findings":  [],          # List of issues
  "remediation": "",     # Step-by-step fix
  "friction_points": "",   # Why AI struggles with it
}}
"""

    # STEP 3: Call Gemini
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
    )

    # STEP 4: Parse output safely (Applying the Regex Fix here too!)
    try:
        # Use Regex to find the JSON block between the first { and last }
        match = re.search(r"\{.*\}", response.text, re.DOTALL)
        clean_json = match.group(0) if match else response.text
        result = json.loads(clean_json)

    except Exception as e:
        print(f"DEBUG: Analyze Parsing failed. Raw: {response.text}")
        return {
            "status_code": 503,
            "API_NAME": api_name,
            "SCORE": [0, 0, 0, 0, 0, 0],  # Ensure we return the expected list format
            "COMMENT": "AI returned malformed data. Try again.",
        }

    return {
        "status_code": result.get("status_code"),
        "API_NAME": api_name,
        "SCORE": result.get("score"),
        "COMMENT": result.get("comment"),
        "findings": result.get("findings"),  # List of issues
        "remediation": result.get("remediation"),  # Step-by-step fix
        "friction_points": result.get("friction_points"),  # Why AI struggles with it
    }


def evaluate_api(api_name: str) -> dict:
    """
    Reduced evaluator:
    Calls the API, then asks Gemini to return ONLY:
    - overall score (0–10)
    - status code
    """

    api_doc = api_name

    # ---------- INTERNAL HELPER FUNCTION ----------
    def call_api(api_url: str) -> str:
        try:
            res = requests.get(api_url, timeout=10)

            try:
                return json.dumps(res.json(), indent=2)
            except Exception:
                return res.text

        except requests.exceptions.RequestException as e:
            return f"ERROR: {str(e)}"

    # ------------------------------------------------

    # STEP 1: Call API
    api_response = call_api(api_name)

    # STEP 2: Reduced Gemini prompt
    prompt = f"""
You are a strict API evaluator.

TASK:
Evaluate the API response quality.

RULES:

If the response contains ANY error:
- Score MUST be 0
- "status_code": integer indicating the overall health of the API request 
• 200 – OK 
• 400 – Faulty input 
• 401 – Unauthorized (private API without key) 
• 422 – Dead/unresponsive links 
• 503 – Service Unavailable (e.g. Gemini is down)

If the response is valid:
- Give ONE overall score from 1–10
- Assign status_code = 200

INPUTS:

API_DOCUMENTATION:
{api_doc}

API_RESPONSE:
{api_response}

OUTPUT FORMAT (STRICT):
Return ONLY JSON:

{{
  "score": int,
  "status_code": int
}}

Example:
{{
  "score": 7,
  "status_code": 200
}}
"""

    # STEP 3: Call Gemini
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
    )

    # STEP 4: Parse output
    try:
        # 1. Look for anything between { and }
        match = re.search(r"\{.*\}", response.text, re.DOTALL)
        if match:
            clean_json = match.group(0)
            result = json.loads(clean_json)
        else:
            # Fallback if no brackets are found
            result = json.loads(response.text)

    except Exception as e:
        print(
            f"DEBUG: Parsing failed. Raw response: {response.text}"
        )  # Helpful for logs
        return {
            "status_code": 503,
            "API_NAME": api_name,
            "SCORE": 0,
        }

    return {
        "status_code": result.get("status_code", 200),  # Default to 200 if missing
        "API_NAME": api_name,
        "SCORE": result.get("score", 0),
    }
