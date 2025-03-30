import google.generativeai as genai
from secret import GEMINI_API_KEY

def get_top_fish(longitude, latitude):
    # Configure the GenAI client
    genai.configure(api_key=GEMINI_API_KEY)

    # Select the model
    model = genai.GenerativeModel('gemini-1.5-flash-latest') # Try another common model

    # Construct the prompt
    prompt = (
        f"List only the names of the top 5 fish species commonly found at longitude {longitude} and latitude {latitude}. "
        "Provide the list separated by newlines. Do not include any introductory text, explanations, or numbering."
    )

    try:
        # Call the Google GenAI API
        response = model.generate_content(prompt)

        # Extract the response text
        # Ensure response.text exists and is not empty before splitting
        if response.text:
            fish_list = response.text.split("\n")
            return [fish.strip() for fish in fish_list if fish.strip()]
        else:
            print("Received empty response from Google GenAI API.")
            return []
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