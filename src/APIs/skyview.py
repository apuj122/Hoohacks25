import requests

def get_star_data(latitude, longitude, time):
    url = f"https://skyview.gsfc.nasa.gov/api/v1?lat={latitude}&lon={longitude}&time={time}"
    response = requests.get(url)
    return response.json()
