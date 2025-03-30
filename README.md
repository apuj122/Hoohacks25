# Adventure Companion Web App

This project provides a web interface for various outdoor adventure and identification tools powered by the Google Gemini API.

## Features

*   **Plan a Trip:**
    *   Find nearby adventure spots (Hiking Trails, Fishing Spots, Campsites, Parks, Scenic Viewpoints, Kayaking/Canoeing Launch Points, Mountain Biking Trails) based on latitude, longitude, and search radius (in miles).
    *   Displays results on an interactive map (`adventure_map.html`) with multiple base map layers (Street, Terrain, Satellite, etc.) and toggles for each location category.
*   **On My Trip Fun:**
    *   **Image Identification:** Upload an image to identify Animals, Birds, or Plants/Flowers. Provides common name, scientific name, locations, and a fun fact.
    *   **Local Fish Info:** Get a list of common fish species found near specific coordinates (uses default coordinates if none provided).
    *   **Astronomy Info:** Get current astronomy-related information (implementation details depend on the original `src/APIs/app.py` script).

## Project Structure

*   `backend_app.py`: The Python Flask web server that handles API requests and runs the backend scripts.
*   `frontend_web/`: Contains the HTML, CSS, and JavaScript files for the web user interface.
    *   `index.html`: Welcome page.
    *   `plan_trip.html`: Interface for the adventure map planner.
    *   `on_trip.html`: Interface for identification and local info tools.
    *   `style.css`: Basic styling for the web pages.
    *   `main.js`: JavaScript for handling user interactions and API calls.
*   `src/APIs/`: Contains the core Python scripts that interact with the Google Gemini API.
    *   `adventure_finder.py`: Finds and maps adventure spots.
    *   `animal_identification.py`: Identifies animals from images.
    *   `bird_identification.py`: Identifies birds from images.
    *   `flora_identification.py`: Identifies plants/flowers from images.
    *   `fishy.py`: Gets local fish information.
    *   `app.py`: Provides astronomy information (original script).
    *   `secret.py`: **(Crucial)** Stores your `GEMINI_API_KEY`. You need to create this file.
    *   `images/`: Contains sample images used for testing.
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
5.  **Create `secret.py`:**
    *   Create a file named `secret.py` inside the `src/APIs/` directory.
    *   Add your Google Gemini API key to this file like this:
        ```python
        # src/APIs/secret.py
        GEMINI_API_KEY = "YOUR_API_KEY_HERE"
        ```
    *   Replace `"YOUR_API_KEY_HERE"` with your actual key. **Do not commit this file to public repositories.** Add `src/APIs/secret.py` to your `.gitignore` file.

## Running the Application

1.  **Start the Backend Server:**
    *   Open your terminal in the project's root directory (where `backend_app.py` is located).
    *   Run the Flask server:
        ```bash
        python backend_app.py
        ```
    *   The server will start, usually on `http://127.0.0.1:5001`.

2.  **Access the Web Interface:**
    *   Open your web browser and navigate to `http://127.0.0.1:5001` or `http://localhost:5001`.

## Usage

*   From the welcome page, choose either "Plan a New Trip" or "On My Trip Fun".
*   **Plan a Trip:** Enter latitude, longitude, and radius (miles), then click "Find Adventures!". The map will be generated and displayed below. Use the layer control (top-right) to switch base maps or toggle location types.
*   **On My Trip Fun:**
    *   **Identification:** Click "Choose File", select an image, then click the appropriate "Identify" button (Animal, Bird, or Plant/Flower). Results will appear below.
    *   **Local Info:** Optionally enter coordinates, then click "Get Local Fish Info" or "Get Astronomy Info". Results will appear below.