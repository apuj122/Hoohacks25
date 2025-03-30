import google.generativeai as genai
import folium
import json
import argparse
import sys
import os
from secret import GEMINI_API_KEY

# --- Argument Parsing ---
parser = argparse.ArgumentParser(description="Find and map nearby adventure spots.")
parser.add_argument("latitude", type=float, help="Latitude of the location.")
parser.add_argument("longitude", type=float, help="Longitude of the location.")
parser.add_argument("--radius_km", type=int, default=25, help="Search radius in kilometers (default: 25).")
parser.add_argument("--output", default="adventure_map.html", help="Output HTML map file name (default: adventure_map.html).")
args = parser.parse_args()

latitude = args.latitude
longitude = args.longitude
radius_km = args.radius_km
output_file = args.output

# --- Configuration ---
# Set up the API key
try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error configuring GenAI: {e}", file=sys.stderr)
    sys.exit(1)

# --- Model Interaction ---
# Load the Gemini model
try:
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
except Exception as e:
    print(f"Error loading model: {e}", file=sys.stderr)
    sys.exit(1)

# Construct the prompt for JSON output with coordinates
prompt = f"""
You are an expert local guide specializing in outdoor adventures.
Find hiking trails, fishing spots, and campsites within approximately {radius_km} km of latitude {latitude}, longitude {longitude}.

Respond ONLY with a valid JSON object containing a single key "locations".
The value of "locations" should be a list of JSON objects, where each object represents a location and has the following keys:
- "name": The name of the location (e.g., "Pine Creek Trail", "Mirror Lake Fishing Spot", "Green Valley Campground").
- "type": The type of location (e.g., "Hiking Trail", "Fishing Spot", "Campsite").
- "latitude": The latitude of the location (float).
- "longitude": The longitude of the location (float).

Example JSON format:
{{
  "locations": [
    {{
      "name": "Example Trail Head",
      "type": "Hiking Trail",
      "latitude": {latitude + 0.01},
      "longitude": {longitude + 0.01}
    }},
    {{
      "name": "Example Fishing Pier",
      "type": "Fishing Spot",
      "latitude": {latitude - 0.01},
      "longitude": {longitude - 0.01}
    }}
  ]
}}

Ensure the coordinates are as accurate as possible. Do not include any text before or after the JSON object. If no locations are found, return an empty list: {{"locations": []}}.
"""

# --- API Call and Response Handling ---
adventure_locations = []
try:
    response = model.generate_content(prompt)

    if response.text:
        json_text = response.text.strip().removeprefix("```json").removesuffix("```").strip()
        data = json.loads(json_text)
        if "locations" in data and isinstance(data["locations"], list):
            adventure_locations = data["locations"]
        else:
            print("Warning: JSON response received, but 'locations' key is missing or not a list.", file=sys.stderr)
            print(f"Raw response: {json_text}", file=sys.stderr)

    else:
        print("Warning: Received empty response from API.", file=sys.stderr)

except json.JSONDecodeError:
    print(f"Error: Failed to parse JSON response from API.", file=sys.stderr)
    print(f"Raw response: {response.text if 'response' in locals() and hasattr(response, 'text') else 'No response text available.'}", file=sys.stderr)
except Exception as e:
    print(f"An error occurred during API call: {e}", file=sys.stderr)

# --- Mapping ---
if adventure_locations:
    print(f"Found {len(adventure_locations)} adventure spots. Generating map...")
    try:
        # Create a map centered at the input location
        m = folium.Map(location=[latitude, longitude], zoom_start=11)

        # Add markers for each location
        for loc in adventure_locations:
            try:
                loc_lat = float(loc.get("latitude", 0))
                loc_lon = float(loc.get("longitude", 0))
                loc_name = loc.get("name", "Unknown Location")
                loc_type = loc.get("type", "Unknown Type")

                if loc_lat != 0 and loc_lon != 0: # Basic check for valid coordinates
                    popup_text = f"<b>{loc_name}</b><br>Type: {loc_type}<br>Lat: {loc_lat:.4f}, Lon: {loc_lon:.4f}"
                    # Choose marker color based on type
                    color = "blue" # Default
                    if loc_type == "Hiking Trail":
                        color = "green"
                    elif loc_type == "Fishing Spot":
                        color = "blue"
                    elif loc_type == "Campsite":
                        color = "orange"

                    folium.Marker(
                        location=[loc_lat, loc_lon],
                        popup=popup_text,
                        tooltip=loc_name,
                        icon=folium.Icon(color=color)
                    ).add_to(m)
                else:
                     print(f"Warning: Skipping location '{loc_name}' due to invalid coordinates ({loc.get('latitude')}, {loc.get('longitude')}).", file=sys.stderr)

            except (ValueError, TypeError) as e:
                print(f"Warning: Could not process location data: {loc}. Error: {e}", file=sys.stderr)
            except Exception as e:
                 print(f"Warning: An unexpected error occurred processing location: {loc}. Error: {e}", file=sys.stderr)


        # Save the map to an HTML file
        m.save(output_file)
        print(f"Map successfully saved to: {os.path.abspath(output_file)}")

    except ImportError:
        print("Error: The 'folium' library is required for mapping. Please install it using 'pip install folium'.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred during map generation: {e}", file=sys.stderr)
else:
    print("No adventure locations found or retrieved to map.")