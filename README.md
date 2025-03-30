# Adventure Companion Web App

This project provides a web interface for various outdoor adventure and identification tools powered by the Google Gemini API and other services.

## Features

*   **Plan a Trip:**
    *   Find nearby adventure spots (Hiking Trails, Fishing Spots, Campsites, Parks, Scenic Viewpoints, Kayaking/Canoeing Launch Points, Mountain Biking Trails) based on latitude/longitude or city name, and search radius (in miles).
    *   Displays results on an interactive map (`adventure_map.html`) with multiple base map layers (Street, Terrain, Satellite, etc.) and toggles for each location category.
*   **On My Trip Fun:**
    *   **Image Identification:** Upload an image to identify Animals, Birds, or Plants/Flowers. Provides common name, scientific name, locations, and a fun fact.
    *   **Local Info:** Get a list of common fish species or an astronomy star chart URL based on coordinates, city name, or your current location (via IP lookup as fallback).

## Project Structure

*   `backend_app.py`: The Python Flask web server that handles API requests, performs geocoding, and runs the backend scripts.
*   `frontend_web/`: Contains the HTML, CSS, and JavaScript files for the web user interface.
    *   `index.html`: Welcome page.
    *   `plan_trip.html`: Interface for the adventure map planner.
    *   `on_trip.html`: Interface for identification and local info tools.
    *   `style.css`: Basic styling for the web pages.
    *   `main.js`: JavaScript for handling user interactions and API calls.
*   `src/APIs/`: Contains the core Python scripts and modules.
    *   `adventure_finder.py`: Finds and maps adventure spots (called by backend).
    *   `animal_identification.py`: Identifies animals from images (called by backend).
    *   `bird_identification.py`: Identifies birds from images (called by backend).
    *   `flora_identification.py`: Identifies plants/flowers from images (called by backend).
    *   `fishy.py`: Gets local fish information (called by backend).
    *   `astronomy_api.py`: Module with functions to call Astronomy and IPInfo APIs (used by backend).
    *   `app.py`: Original standalone Flask app for astronomy (no longer used by the main backend).
    *   `secret.py`: (Optional) Can store `GEMINI_API_KEY` if running individual scripts directly. Not used by `backend_app.py`.
    *   `images/`: Contains sample images used for testing.
*   `.env`: **(Crucial)** Stores API keys used by the backend server. **You need to create this file.**
*   `uploads/`: (Created automatically) Temporary storage for uploaded images during identification.
*   `adventure_map.html`: (Generated automatically) The output map file from the "Plan Trip" feature.
*   `requirements.txt`: Lists the required Python libraries.
*   `README.md`: This file.

## Setup

1.  **Clone the Repository:** (If applicable)
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```
2.  **Python:** Ensure you have Python 3 installed.
3.  **Create Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```
4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Create `.env` File:**
    *   Create a file named `.env` in the **project root directory** (the same directory as `backend_app.py`).
    *   Add your API keys to this file, one per line, like this:
        ```dotenv
        # .env file
        GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
        APP_ID="YOUR_ASTRONOMY_APP_ID_HERE"
        APP_SECRET="YOUR_ASTRONOMY_APP_SECRET_HERE"
        API_KEY="YOUR_IPINFO_API_KEY_HERE"
        ```
    *   Replace the placeholder values with your actual keys obtained from Google AI Studio (Gemini), AstronomyAPI.com, and IPinfo.io.
    *   **Important:** Do not commit the `.env` file to public repositories. Add `.env` to your `.gitignore` file.

6.  **(Optional) Create `src/APIs/secret.py`:**
    *   If you intend to run scripts like `fishy.py` or the identification scripts *directly* from the command line (outside the web app), they might still rely on `src/APIs/secret.py`.
    *   If needed, create `src/APIs/secret.py` and add:
        ```python
        # src/APIs/secret.py
        GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
        ```
    *   Add `src/APIs/secret.py` to your `.gitignore` file as well.

## Running the Application

1.  **Start the Backend Server:**
    *   Open your terminal in the project's root directory.
    *   Make sure your virtual environment is activated (if you created one).
    *   Run the Flask server:
        ```bash
        python backend_app.py
        ```
    *   The server will start, usually on `http://127.0.0.1:5001`. It will load the keys from your `.env` file.

2.  **Access the Web Interface:**
    *   Open your web browser and navigate to `http://127.0.0.1:5001` or `http://localhost:5001`.

## Usage

*   From the welcome page, choose either "Plan a New Trip" or "On My Trip Fun".
*   **Plan a Trip:** Select "Coordinates" or "City Name". Enter the required location details and radius (miles), then click "Find Adventures!". The map will be generated and displayed below. Use the layer control (top-right) to switch base maps or toggle location types.
*   **On My Trip Fun:**
    *   **Identification:** Click "Choose File", select an image, then click the appropriate "Identify" button (Animal, Bird, or Plant/Flower). Results will appear below.
    *   **Local Info:** Select "Coordinates" or "City Name". Enter location details (optional, defaults to IP lookup/defaults if blank), then click "Get Local Fish Info" or "Get Astronomy Info". Results will appear below.