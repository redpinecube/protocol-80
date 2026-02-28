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
