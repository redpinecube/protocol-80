from google import genai
from dotenv import load_dotenv
import os

# This finds your .env file and loads the variables into os.environ
load_dotenv()

# Now you can assign it to a Django setting
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

# response = client.models.generate_content(
#     model="gemini-3-flash-preview", contents="recipe for egg fried rice"
# )
#
# print(response.text)

API_DOC = ''
API_RESPONSE = ''

evaluation_prompt = f"""
You are a strict API quality evaluator.

Your task:
Evaluate how AI-friendly, well-structured, and well-documented the API response is, based on the API documentation.

INPUTS:

API_DOCUMENTATION:
{API_DOC}

API_RESPONSE:
{API_RESPONSE}

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
Return ONLY a Python tuple:
(int_score, "short_comment")

Examples:
(0, "Missing required 'id' field. Fix: include all mandatory response fields.")
(7, "Clear structure but field naming could be more descriptive.")
"""



response = client.models.generate_content(
    model="gemini-3-flash-preview", 
    contents=evaluation_prompt
)

