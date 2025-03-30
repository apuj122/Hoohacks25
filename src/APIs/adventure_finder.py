import google.generativeai as genai
import folium
from folium.plugins import MarkerCluster # Can be useful if many points are returned
import json
import argparse
import sys
import os
from collections import defaultdict
from secret import GEMINI_API_KEY

# Conversion factor
MILES_TO_KM = 1.60934

# Define categories and their map styling
CATEGORIES = {
    "Hiking Trail": {"color": "green", "icon": "leaf"},
    "Fishing Spot": {"color": "blue", "icon": "tint"}, # Water drop
    "Campsite": {"color": "orange", "icon": "home"}, # Tent/home icon
    "Park": {"color": "darkgreen", "icon": "tree-conifer"}, # Using glyphicon
    "Scenic Viewpoint": {"color": "purple", "icon": "eye-open"}, # Using glyphicon
    "Kayaking/Canoeing Launch Point": {"color": "cadetblue", "icon": "road"}, # Simple road/launch icon
    "Mountain Biking Trail": {"color": "red", "icon": "bicycle"} # Using glyphicon
}

# --- Argument Parsing ---
parser = argparse.ArgumentParser(description="Find and map nearby adventure spots.")
parser.add_argument("latitude", type=float, help="Latitude of the location.")
parser.add_argument("longitude", type=float, help="Longitude of the location.")
parser.add_argument("--radius_miles", type=float, default=15.0, help="Search radius in miles (default: 15.0).")
parser.add_argument("--output", default="adventure_map.html", help="Output HTML map file name (default: adventure_map.html).")
args = parser.parse_args()

latitude = args.latitude
longitude = args.longitude
radius_miles = args.radius_miles
output_file = args.output

# Convert miles to km for the API prompt
radius_km = radius_miles * MILES_TO_KM

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

# Construct the updated prompt for JSON output with coordinates and top 5 per category
# List all requested categories explicitly
category_list_str = ", ".join(CATEGORIES.keys())
prompt = f"""
You are an expert local guide specializing in outdoor adventures.
Find the top 5 locations for each of the following categories within approximately {radius_km:.1f} km (equivalent to {radius_miles:.1f} miles) of latitude {latitude}, longitude {longitude}:
{category_list_str}.

Respond ONLY with a valid JSON object containing a single key "locations".
The value of "locations" should be a list of JSON objects, where each object represents a location and has the following keys:
- "name": The name of the location.
- "type": The type of location (must be one of: {category_list_str}).
- "latitude": The latitude of the location (float).
- "longitude": The longitude of the location (float).

Aim to provide up to 5 distinct locations for each category if available within the radius.

Example JSON format:
{{
  "locations": [
    {{
      "name": "Example Trail Head",
      "type": "Hiking Trail",
      "latitude": {latitude + 0.01},
      "longitude": {longitude + 0.01}
    }},
    // ... up to 5 hiking trails
    {{
      "name": "Example Park Entrance",
      "type": "Park",
      "latitude": {latitude + 0.015},
      "longitude": {longitude - 0.015}
    }},
    // ... up to 5 parks
    {{
      "name": "Example Scenic Overlook",
      "type": "Scenic Viewpoint",
      "latitude": {latitude - 0.01},
      "longitude": {longitude + 0.01}
    }},
    // ... up to 5 viewpoints
    // ... etc. for all requested categories
  ]
}}

Ensure the coordinates are as accurate as possible. Do not include any text before or after the JSON object. If no locations are found for a category or overall, return an empty list or fewer items as appropriate: {{"locations": []}}.
"""

# --- API Call and Response Handling ---
adventure_locations = []
try:
    # Increased potential response size as we ask for more items
    generation_config = genai.types.GenerationConfig(max_output_tokens=4096) # Increased token limit
    response = model.generate_content(prompt, generation_config=generation_config)

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
        # Start with the default OpenStreetMap tiles
        zoom_level = 11 if radius_miles <= 20 else 10
        m = folium.Map(location=[latitude, longitude], zoom_start=zoom_level, tiles="OpenStreetMap")

        # --- Add Additional Base Map Tile Layers ---
        # Stamen Terrain
        folium.TileLayer(
            tiles='Stamen Terrain',
            attr='Map tiles by Stamen Design, CC BY 3.0 — Map data © OpenStreetMap contributors',
            name='Terrain'
        ).add_to(m)

        # CartoDB Positron (Light)
        folium.TileLayer(
            tiles='CartoDB positron',
            attr='Map tiles by CartoDB, under CC BY 3.0. Data by OpenStreetMap, under ODbL.',
            name='Light Map'
        ).add_to(m)

        # CartoDB Dark Matter (Dark)
        folium.TileLayer(
            tiles='CartoDB dark_matter',
            attr='Map tiles by CartoDB, under CC BY 3.0. Data by OpenStreetMap, under ODbL.',
            name='Dark Map'
        ).add_to(m)

        # Esri World Imagery (Satellite) - Often works without API key for basic use
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
            name='Satellite'
        ).add_to(m)


        # --- Create Feature Groups for Location Categories ---
        feature_groups = defaultdict(lambda: folium.FeatureGroup(name="Unknown Category", show=False)) # Start with category layers potentially hidden
        for cat_name in CATEGORIES.keys():
             # Use the category name directly for the layer control label
            feature_groups[cat_name] = folium.FeatureGroup(name=cat_name)

        # Add markers to the appropriate feature group
        for loc in adventure_locations:
            try:
                loc_lat = float(loc.get("latitude", 0))
                loc_lon = float(loc.get("longitude", 0))
                loc_name = loc.get("name", "Unknown Location")
                loc_type = loc.get("type", "Unknown Category") # Default if type is missing/invalid

                if loc_lat != 0 and loc_lon != 0: # Basic check for valid coordinates
                    popup_text = f"<b>{loc_name}</b><br>Type: {loc_type}<br>Lat: {loc_lat:.4f}, Lon: {loc_lon:.4f}"

                    # Get style from CATEGORIES, default if type unknown
                    style = CATEGORIES.get(loc_type, {"color": "gray", "icon": "question-sign"})

                    marker = folium.Marker(
                        location=[loc_lat, loc_lon],
                        popup=popup_text,
                        tooltip=loc_name,
                        icon=folium.Icon(color=style["color"], icon=style["icon"], prefix='glyphicon')
                    )

                    # Add marker to the correct feature group
                    if loc_type in feature_groups:
                        marker.add_to(feature_groups[loc_type])
                    else:
                         # Add to a default 'Unknown' group if type doesn't match known categories
                         print(f"Warning: Location '{loc_name}' has unknown type '{loc_type}'. Adding to 'Unknown Category' group.", file=sys.stderr)
                         marker.add_to(feature_groups["Unknown Category"])

                else:
                     print(f"Warning: Skipping location '{loc_name}' due to invalid coordinates ({loc.get('latitude')}, {loc.get('longitude')}).", file=sys.stderr)

            except (ValueError, TypeError) as e:
                print(f"Warning: Could not process location data: {loc}. Error: {e}", file=sys.stderr)
            except Exception as e:
                 print(f"Warning: An unexpected error occurred processing location: {loc}. Error: {e}", file=sys.stderr)

        # Add all feature groups to the map
        for group in feature_groups.values():
            group.add_to(m)

        # Add layer control (toggles) to the map
        folium.LayerControl().add_to(m)

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