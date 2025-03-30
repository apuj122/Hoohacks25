import os
import base64
import requests
import datetime
import sys

# Note: This script now expects credentials (APP_ID, APP_SECRET, API_KEY)
# to be loaded into the environment by the calling script (e.g., backend_app.py using dotenv).

ASTRONOMY_API_URL = 'https://api.astronomyapi.com/api/v2/studio/star-chart'

def get_auth_string(app_id, app_secret):
    """Encodes app_id and app_secret for Basic Authentication."""
    if not app_id or not app_secret:
        return None
    userpass = f"{app_id}:{app_secret}"
    return base64.b64encode(userpass.encode()).decode()

def get_location_from_ip(ip_address, ipinfo_api_key):
    """Gets location data (lat, lon) from IP address using ipinfo.io."""
    if not ipinfo_api_key:
        print("Warning: IPInfo API Key not provided. Cannot determine location from IP.", file=sys.stderr)
        # Return default or None, depending on how you want to handle this
        return None # Or some default location dictionary

    # Use a default IP if none provided or if it's a local IP? For testing.
    # Using a known public IP for testing if needed: '199.111.224.91'
    url = f"https://ipinfo.io/{ip_address}/json?token={ipinfo_api_key}"

    try:
        response = requests.get(url, timeout=5) # Add timeout
        response.raise_for_status()
        data = response.json()
        print("IPInfo API Response:", data, file=sys.stderr) # Debugging

        if 'loc' in data:
            latitude, longitude = map(float, data['loc'].split(','))
            return {
                "latitude": latitude,
                "longitude": longitude,
                "city": data.get("city"),
                "region": data.get("region"),
                "country": data.get("country"),
                "timezone": data.get("timezone"),
            }
        else:
            print(f"Warning: No 'loc' field found in ipinfo response for IP {ip_address}.", file=sys.stderr)
            return None
    except requests.exceptions.Timeout:
        print(f"Error: Timeout connecting to ipinfo.io for IP {ip_address}", file=sys.stderr)
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching location from ipinfo.io: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Unexpected error in get_location_from_ip: {e}", file=sys.stderr)
        return None


def get_star_chart_image_url(latitude, longitude, date_str=None, style="default", app_id=None, app_secret=None):
    """Generates a star chart using the Astronomy API and returns the image URL."""
    auth_string = get_auth_string(app_id, app_secret)
    if not auth_string:
        return {"error": "Astronomy API credentials (APP_ID, APP_SECRET) missing."}

    headers = {
        "Authorization": f"Basic {auth_string}",
        "Content-Type": "application/json"
    }

    if date_str is None:
        date_str = datetime.date.today().strftime("%Y-%m-%d")

    payload = {
        "style": style,
        "observer": {
            "latitude": latitude,
            "longitude": longitude,
            "date": date_str
        },
        "view": {
            "type": "area",
            "parameters": {
                "position": {
                    "equatorial": {
                        # Default view - can be customized if needed
                        "rightAscension": 1,
                        "declination": latitude # Center roughly on observer's latitude
                    }
                },
                "zoom": 2 # Adjust zoom as needed
            }
        }
    }

    try:
        # Increase timeout to 30 seconds
        response = requests.post(ASTRONOMY_API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        response_data = response.json()
        if 'data' in response_data and 'imageUrl' in response_data['data']:
            return {"success": True, "image_url": response_data['data']['imageUrl']}
        else:
            print(f"Astronomy API response missing expected data: {response_data}", file=sys.stderr)
            return {"error": "Astronomy API response format unexpected.", "details": response_data}

    except requests.exceptions.Timeout:
        print("Error: Timeout connecting to Astronomy API.", file=sys.stderr)
        return {"error": "Timeout connecting to Astronomy API."}
    except requests.exceptions.RequestException as e:
        error_details = e.response.text if e.response else str(e)
        print(f"Error calling Astronomy API: {e}", file=sys.stderr)
        print(f"Response: {error_details}", file=sys.stderr)
        return {"error": "Failed to generate star map.", "details": error_details}
    except Exception as e:
        print(f"Unexpected error in get_star_chart_image_url: {e}", file=sys.stderr)
        return {"error": f"An unexpected error occurred: {e}"}

# Example function for constellation - can be expanded similarly
# def get_constellation_image_url(latitude, longitude, constellation_code, date_str=None, style="default", app_id=None, app_secret=None):
#     # ... similar logic using "type": "constellation" and "parameters": {"constellation": constellation_code} ...
#     pass