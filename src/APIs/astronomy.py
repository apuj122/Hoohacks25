import os
import base64
import requests
from dotenv import load_dotenv

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

# Encode to base64
authString = base64.b64encode(userpass.encode()).decode()

# API URL for star chart generation
url = 'https://api.astronomyapi.com/api/v2/studio/star-chart'

# Headers with authorization
headers = {
    "Authorization": f"Basic {authString}",
    "Content-Type": "application/json"
}

# Data for skyMap
skyMap = {
    "style": "default",
    "observer": {
        "latitude": 33.775867,  # Replace with actual latitude
        "longitude": -84.39733,  # Replace with actual longitude
        "date": "2019-12-20"     # Replace with actual date
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
            "zoom": 3
        }
    }
}
consetellation = {
    "style": "default",
    "observer": {
        "latitude": 33.775867,  # Replace with actual latitude
        "longitude": -84.39733,  # Replace with actual longitude
        "date": "2019-12-20"     # Replace with actual date
    },
    "view": {
        "type": "constellation",  # You can change this to "area" if you want
        "parameters": {
            "constellation": "vir"  # Example for Orion constellation (change as needed)
        }
    }
}


# Make the POST request to the API
responseMap = requests.post(url, json=skyMap, headers=headers)
consetellation = requests.post(url, json=consetellation, headers=headers)

# Handle the response
if (responseMap.status_code and consetellation.status_code) == 200:
    response_map = responseMap.json()
    response_const =consetellation.json()
    print("Star Map generated successfully.")
    print("Image URL:", response_map['data']['imageUrl'])
    print("Constellation generated successfully.")
    print("Image URL:", response_const['data']['imageUrl'])
else:
    print(f"Failed with status code {responseMap.status_code}: {responseMap.text}")
