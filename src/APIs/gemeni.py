from google import genai
from APIs.secret import GEMINI_API_KEY

client = genai.Client(api_key= GEMINI_API_KEY)

def generate_gemini_response(prompt):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response