from google.generativeai import chat
from APIs.secret import GEMINI_API_KEY

def get_top_fish(longitude, latitude):
    # Replace with your Google GenAI API key
    chat.api_key = GEMINI_API_KEY

    # Construct the prompt
    prompt = (
        f"Given the longitude {longitude} and latitude {latitude}, "
        "list the top 5 fish species commonly found in this area."
    )

    try:
        # Call the Google GenAI API
        response = chat.generate_text(
            prompt=prompt,
            temperature=0.7,
            max_output_tokens=100
        )
        # Extract the response text
        fish_list = response.result.split("\n")
        return [fish.strip() for fish in fish_list if fish.strip()]
    except Exception as e:
        print(f"Error fetching data from Google GenAI API: {e}")
        return []

if __name__ == "__main__":
    # Example coordinates (replace with actual user location)
    user_longitude = -77.0364
    user_latitude = 38.8951

    top_fish = get_top_fish(user_longitude, user_latitude)
    if top_fish:
        print("Top 5 fish in your area:")
        for i, fish in enumerate(top_fish, start=1):
            print(f"{i}. {fish}")
    else:
        print("No fish data available for your area.")