import google.generativeai as genai
import base64
import json
from secret import GEMINI_API_KEY

# Set up the API key
genai.configure(api_key=GEMINI_API_KEY)

# Convert the image to Base64
def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# Load the Gemini model
model = genai.GenerativeModel("gemini-pro-vision")

# Image path
image_path = "your_image.jpg"

# Send request with image and text
response = model.generate_content([
    {"type": "text", "text": "You are a professional on animals. Identify the animal in this image and provide the following details: Common Name, Scientific Name, Places this animal can be found (comma-separated list), and one fun fact about this animal."},
    {"type": "image", "data": encode_image(image_path)}
])

# Extract relevant information from the response
# Assuming the response contains the required fields in a structured format
result = {
    "Common Name": response.get("common_name", "Unknown"),
    "Scientific Name": response.get("scientific_name", "Unknown"),
    "Places Found": response.get("places_found", "Unknown"),
    "Fun Fact": response.get("fun_fact", "Unknown")
}

# Return the result as JSON
print(json.dumps(result, indent=4))
