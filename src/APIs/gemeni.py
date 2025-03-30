from google import genai
from google.genai import types
from APIs.secret import GEMINI_API_KEY

client = genai.Client(api_key= GEMINI_API_KEY)

def generate_gemini_response(prompt, tool):
    tools = types.Tool(function_declarations=[tool])
    config = types.GenerateContentConfig(tools = [tools])
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=config
    )
    
    return response