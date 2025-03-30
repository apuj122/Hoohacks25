import google.generativeai as genai
import base64
import json
import argparse
import sys
from secret import GEMINI_API_KEY

# --- Argument Parsing ---
parser = argparse.ArgumentParser(description="Identify an animal from an image.")
parser.add_argument("image_path", help="Path to the animal image file.")
args = parser.parse_args()
image_path = args.image_path

# --- Configuration ---
# Set up the API key
try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error configuring GenAI: {e}", file=sys.stderr)
    sys.exit(1)

# --- Image Encoding ---
# Convert the image to Base64
def encode_image(filepath):
    try:
        with open(filepath, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"Error: Image file not found at {filepath}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error encoding image: {e}", file=sys.stderr)
        sys.exit(1)

# --- Model Interaction ---
# Load the Gemini model
try:
    model = genai.GenerativeModel("gemini-1.5-flash-latest") # Use a current vision model
except Exception as e:
    print(f"Error loading model: {e}", file=sys.stderr)
    sys.exit(1)

# Encode the image
encoded_image = encode_image(image_path)

# Construct the prompt parts for multimodal input
prompt_parts = [
    # Text prompt first
    """You are a professional zoologist. Identify the animal in the provided image.
Respond ONLY with a valid JSON object containing the following keys:
- "common_name": The common name of the animal.
- "scientific_name": The scientific name of the animal.
- "places_found": A comma-separated string listing common locations/habitats.
- "fun_fact": One interesting fact about the animal.

Example JSON format:
{
  "common_name": "Red Fox",
  "scientific_name": "Vulpes vulpes",
  "places_found": "Northern Hemisphere, Australia",
  "fun_fact": "Red foxes use the Earth's magnetic field to hunt."
}

Do not include any text before or after the JSON object.""",
    # Image part next, structured as inline_data
    {
        "inline_data": {
            "mime_type": "image/jpeg", # Assuming JPEG, adjust if needed for other formats
            "data": encoded_image
        }
    }
]

# --- API Call and Response Handling ---
try:
    # Send request with image and text
    response = model.generate_content(prompt_parts)

    # Extract and parse the JSON response text
    if response.text:
        # Clean potential markdown code block fences
        json_text = response.text.strip().removeprefix("```json").removesuffix("```").strip()
        result = json.loads(json_text)
    else:
        result = {
            "error": "Received empty response from API."
        }

except json.JSONDecodeError:
    result = {
        "error": "Failed to parse JSON response from API.",
        "raw_response": response.text if 'response' in locals() and hasattr(response, 'text') else "No response text available."
    }
except Exception as e:
    result = {
        "error": f"An error occurred during API call: {e}"
    }

# --- Output ---
# Return the result as JSON
print(json.dumps(result, indent=4))
