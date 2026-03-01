from google import genai
from dotenv import load_dotenv
import os
import json

# This finds your .env file and loads the variables into os.environ
load_dotenv()

# Now you can assign it to a Django setting
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

# example usage:
# response = client.models.generate_content(
#     model="gemini-3-flash-preview", contents="recipe for egg fried rice"
# )
# print(response.text)

evaluation_prompt = f"""

EVALUATION CRITERIA:

If the response contains an error:
- Score MUST be 0
- Comment must:
    • Clearly state what the error is
    • Provide ONE short possible fix

If the response is valid:
Score from 1 to 10 based on:

1. Structural clarity (JSON consistency, predictable schema)
2. Completeness (all documented fields returned)
3. Documentation alignment (matches documented contract)
4. Naming clarity (clear, unambiguous fields)
5. AI-friendliness (machine-readable, minimal ambiguity)

SCORING GUIDE:
1–3 = Poorly structured, unclear, or inconsistent
4–6 = Functional but lacks clarity or consistency
7–8 = Well structured with minor improvements possible
9–10 = Excellent structure, fully aligned, highly AI-friendly

COMMENT REQUIREMENTS:
- One concise evaluation
- If valid, include ONE specific improvement suggestion

OUTPUT FORMAT (STRICT):
Return ONLY a JSON object with the following keys:

- "score": integer (0-10) following the scoring rules above
- "comment": string containing the evaluation or improvement suggestion
- "status_code": integer indicating the overall health of the API request
    • 200 – OK
    • 400 – Faulty input
    • 401 – Unauthorized (private API without key)
    • 422 – Dead/unresponsive links
    • 503 – Service Unavailable (e.g. Gemini is down)

Examples of valid outputs:
  "score": 0,
  "comment": "Missing required 'id' field. Fix: include all mandatory response fields.",
  "status_code": 400


  "score": 7,
  "comment": "Clear structure but field naming could be more descriptive.",
  "status_code": 200

"""





def evaluate_api(api_name: str, api_doc: str, api_response: str) -> dict:
    """Run the Gemini evaluation prompt and return structured results.

    Args:
        api_name: Friendly name of the API being evaluated.
        api_doc: The documentation string for the API.
        api_response: The raw response returned by the API.

    Returns:
        A dictionary with keys ``status_code``, ``API_NAME``, ``SCORE``, ``COMMENT``.
    """

    # build prompt with provided inputs
    prompt = f"""
You are a strict API quality evaluator.

Your task:
Evaluate how AI-friendly, well-structured, and well-documented the API response is, based on the API documentation.

INPUTS:

API_DOCUMENTATION:
{api_doc}

API_RESPONSE:
{api_response}

{evaluation_prompt.split('OUTPUT FORMAT')[1]}
"""

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
    )

    # parse the JSON output from the model
    try:
        result = json.loads(response.text)
    except Exception:
        # if parsing fails, treat as error
        return {
            "status_code": 503,
            "API_NAME": api_name,
            "SCORE": 0,
            "COMMENT": "Unable to parse evaluator output",
        }

    return {
        "status_code": result.get("status_code"),
        "API_NAME": api_name,
        "SCORE": result.get("score"),
        "COMMENT": result.get("comment"),
    }

