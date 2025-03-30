import os
import base64
import requests
from flask import Flask, request, jsonify, redirect, url_for
from dotenv import load_dotenv

# Initialize Flask app
app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Fetch the credentials from environment variables
app_id = os.getenv('APP_ID')
app_secret = os.getenv('APP_SECRET')

# Check if the variables were loaded correctly
if not app_id or not app_secret:
    raise ValueError("Application ID and/or Secret not found in .env file")

# Combine them into the format "applicationId:applicationSecret"
userpass = f"{app_id}:{app_secret}"

# Encode to base64 for Basic Authentication
authString = base64.b64encode(userpass.encode()).decode()

# API URL for star chart generation
url = 'https://api.astronomyapi.com/api/v2/studio/star-chart'

# Headers with authorization
headers = {
    "Authorization": f"Basic {authString}",
    "Content-Type": "application/json"
}

# Function to get location information based on IP
def get_location(ip_address):
    api_key = os.getenv('API_KEY') # Replace with your own token if needed
    url = f"https://ipinfo.io/199.111.224.91/json?token={api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Print API response for debugging
        print("API Response:", data)

        # Extract latitude and longitude if available
        if 'loc' in data:
            latitude, longitude = map(float, data['loc'].split(','))
            return {
                "latitude": latitude,
                "longitude": longitude,
                "city": data.get("city", "Unknown"),
                "region": data.get("region", "Unknown"),
                "country": data.get("country", "Unknown"),
                "timezone": data.get("timezone", "Unknown"),
                "ip": data.get("ip", "Unknown"),
                "isp": data.get("org", "Unknown")
            }
        else:
            return {"error": "No location data found.", "full_response": data}

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Route to get location based on client's IP
@app.route('/get-starmap', methods=['GET'])
def get_client_location():
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    location_data = get_location(ip_address)

    if "latitude" in location_data and "longitude" in location_data:
        # Use the retrieved latitude and longitude in the star chart request
        skyMap = {
            "style": "default",
            "observer": {
                "latitude": location_data["latitude"],  # Dynamic latitude
                "longitude": location_data["longitude"],  # Dynamic longitude
                "date": "2025-03-30"  # Use current date or change as needed
            },
            "view": {
                "type": "area",
                "parameters": {
                    "position": {
                        "equatorial": {
                            "rightAscension": 14.83,
                            "declination": -15.23
                        }
                    },
                    "zoom": 10
                }
            }
        }
        
        # Make the POST request to the Astronomy API to generate the star chart
        responseMap = requests.post(url, json=skyMap, headers=headers)

        if responseMap.status_code == 200:
            response_map = responseMap.json()
            return jsonify({
                "message": "Star map generated successfully.",
                "image_url": response_map['data']['imageUrl']
            })
        else:
            return jsonify({
                "error": "Failed to generate star map.",
                "status_code": responseMap.status_code,
                "response": responseMap.text
            })
    else:
        return jsonify(location_data)
    
@app.route('/get-constellation', methods=['GET'])
def get_const_location():
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    location_data = get_location(ip_address)

    if "latitude" in location_data and "longitude" in location_data:
        # Use the retrieved latitude and longitude in the star chart request
        skyCon= {
            "style": "default",
            "observer": {
                "latitude": location_data["latitude"],  # Dynamic latitude
                "longitude": location_data["longitude"],  # Dynamic longitude
                "date": "2025-03-30"  # Use current date or change as needed
            },
            "view": {
                "type": "constellation",  # You can change this to "area" if you want
                "parameters": {
                    "constellation": "ori"  # Example for Orion constellation (change as needed)
                }
            }
        }
        
        # Make the POST request to the Astronomy API to generate the star chart
        responseConstellation = requests.post(url, json=skyCon, headers=headers)

        if responseConstellation.status_code == 200:
            response_con = responseConstellation.json()
            return jsonify({
                "message": "Star map generated successfully.",
                "image_url": response_con['data']['imageUrl']
            })
        else:
            return jsonify({
                "error": "Failed to generate star map.",
                "status_code": responseConstellation.status_code,
                "response": responseConstellation.text
            })
    else:
        return jsonify(location_data)

# Home route that redirects to get-location
@app.route('/')
def home():
    return redirect(url_for('get_client_location'))


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
