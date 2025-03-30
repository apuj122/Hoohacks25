import subprocess
import os
import json
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import sys
from dotenv import load_dotenv

# Load environment variables from .env file in the project root
load_dotenv()

# Import refactored astronomy functions
from src.APIs.astronomy_api import get_location_from_ip, get_star_chart_image_url

# --- Configuration ---
# Assuming your scripts are in src/APIs relative to this backend file
SCRIPT_DIR = os.path.join(os.path.dirname(__file__), 'src', 'APIs')
SCRIPT_DIR = os.path.join(os.path.dirname(__file__), 'src', 'APIs')
# Ensure the script directory is in the Python path if scripts import local modules like 'secret'
sys.path.insert(0, SCRIPT_DIR)

# Define upload folder for identification images
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Define the output directory for the map (relative to backend_app.py)
MAP_OUTPUT_DIR = os.path.dirname(__file__)
MAP_FILENAME = "adventure_map.html"
MAP_OUTPUT_PATH = os.path.join(MAP_OUTPUT_DIR, MAP_FILENAME)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Helper Function to Run Scripts ---
def run_script(script_name, args_list):
    """Runs a Python script using subprocess and returns its output."""
    script_path = os.path.join(SCRIPT_DIR, script_name)
    command = [sys.executable, script_path] + args_list
    print(f"Running command: {' '.join(command)}", file=sys.stderr) # Log the command being run
    try:
        # Set cwd to the directory containing backend_app.py so relative paths in scripts work as expected
        # (e.g., adventure_finder saving map to MAP_OUTPUT_PATH)
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            cwd=os.path.dirname(__file__) # Run script from the backend app's directory
        )
        print(f"Script {script_name} stdout:\n{process.stdout}", file=sys.stderr)
        print(f"Script {script_name} stderr:\n{process.stderr}", file=sys.stderr)
        return {"success": True, "output": process.stdout, "error": process.stderr}
    except FileNotFoundError:
        error_msg = f"Error: Script '{script_path}' not found."
        print(error_msg, file=sys.stderr)
        return {"success": False, "output": "", "error": error_msg}
    except subprocess.CalledProcessError as e:
        error_msg = f"Error running script {script_name}: {e}\nStderr: {e.stderr}\nStdout: {e.stdout}"
        print(error_msg, file=sys.stderr)
        return {"success": False, "output": e.stdout, "error": error_msg}
    except Exception as e:
        error_msg = f"An unexpected error occurred running {script_name}: {e}"
        print(error_msg, file=sys.stderr)
        return {"success": False, "output": "", "error": error_msg}


# --- API Endpoints ---

@app.route('/api/plan_trip', methods=['POST'])
def plan_trip():
    """Endpoint to generate the adventure map."""
    data = request.json
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    radius_miles = data.get('radius_miles', 15.0) # Default to 15 miles

    if not latitude or not longitude:
        return jsonify({"success": False, "error": "Missing latitude or longitude"}), 400

    try:
        lat_float = float(latitude)
        lon_float = float(longitude)
        radius_float = float(radius_miles)
    except ValueError:
        return jsonify({"success": False, "error": "Invalid numeric input for coordinates or radius"}), 400

    # Arguments for adventure_finder.py
    args = [
        str(lat_float),
        str(lon_float),
        '--radius_miles', str(radius_float),
        '--output', MAP_OUTPUT_PATH # Ensure script saves map where Flask can find it
    ]

    result = run_script('adventure_finder.py', args)

    if result["success"]:
        # Check if the map file was actually created by the script
        if os.path.exists(MAP_OUTPUT_PATH):
             # Return the relative path/URL the frontend can use to fetch the map
            return jsonify({"success": True, "map_url": f"/{MAP_FILENAME}"})
        else:
            error_msg = f"Script executed but map file '{MAP_OUTPUT_PATH}' not found. Script output: {result.get('output', '')} Stderr: {result.get('error', '')}"
            print(error_msg, file=sys.stderr)
            return jsonify({"success": False, "error": error_msg}), 500
    else:
        return jsonify({"success": False, "error": result["error"]}), 500
# Endpoint to serve the generated map file
@app.route(f'/{MAP_FILENAME}')
def serve_map():
    # Ensure the map file exists before trying to serve
    if not os.path.exists(MAP_OUTPUT_PATH):
        return "Map file not found.", 404
    return send_from_directory(MAP_OUTPUT_DIR, MAP_FILENAME)

# --- Static File Serving ---

# Serve the main index.html page
@app.route('/')
def serve_index():
    return send_from_directory('frontend_web', 'index.html')

# Serve other files (HTML, CSS, JS) from the frontend_web directory
@app.route('/<path:filename>')
def serve_frontend_files(filename):
    # Prevent this route from accidentally catching API calls or the map file
    if filename.startswith('api/') or filename == MAP_FILENAME:
        # Let other specific routes handle these
        return "Not Found", 404 # Or use Flask's abort(404)
    return send_from_directory('frontend_web', filename)


# --- API Endpoints ---
# (Existing endpoints remain below)

@app.route('/api/identify', methods=['POST'])
def identify_object():
    """Endpoint to identify animal, bird, or flora from an uploaded image."""
    if 'image' not in request.files:
        return jsonify({"success": False, "error": "No image file provided"}), 400
    if 'id_type' not in request.form:
         return jsonify({"success": False, "error": "Identification type (id_type) missing"}), 400

    file = request.files['image']
    id_type = request.form['id_type']

    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"}), 400

    # Map id_type to script name
    script_map = {
        'animal': 'animal_identification.py',
        'bird': 'bird_identification.py',
        'flora': 'flora_identification.py'
    }

    if id_type not in script_map:
        return jsonify({"success": False, "error": f"Invalid identification type: {id_type}"}), 400

    script_to_run = script_map[id_type]

    if file:
        # Use a more robust temporary file handling approach if possible in production
        # For simplicity here, save to uploads with a unique name
        filename = secure_filename(file.filename)
        unique_filename = f"{os.path.splitext(filename)[0]}_{os.urandom(4).hex()}{os.path.splitext(filename)[1]}"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

        try:
            file.save(image_path)
            print(f"Image saved to: {image_path}", file=sys.stderr)

            # Arguments for identification scripts
            args = [image_path]
            result = run_script(script_to_run, args)

            # Attempt to parse the JSON output from the script
            if result["success"] and result["output"]:
                try:
                    # The script should print only JSON to stdout
                    json_output = json.loads(result["output"])
                    # Check if the script itself returned an error within its JSON
                    if isinstance(json_output, dict) and json_output.get("error"):
                         print(f"Script {script_to_run} reported an error: {json_output['error']}", file=sys.stderr)
                         return jsonify({"success": False, "error": f"Identification failed: {json_output['error']}"}), 500
                    else:
                        return jsonify({"success": True, "data": json_output})
                except json.JSONDecodeError:
                    error_msg = f"Script {script_to_run} ran but output was not valid JSON.\nOutput:\n{result['output']}"
                    print(error_msg, file=sys.stderr)
                    return jsonify({"success": False, "error": error_msg}), 500
            elif not result["success"]:
                 # Include script's stderr if available
                 error_detail = result.get("error", "Unknown script execution error")
                 return jsonify({"success": False, "error": f"Script execution failed: {error_detail}"}), 500
            else: # Success but no output? Should not happen if scripts work
                 return jsonify({"success": False, "error": f"Script {script_to_run} ran successfully but produced no output."}), 500

        except Exception as e:
            error_msg = f"Error processing identification request: {e}"
            print(error_msg, file=sys.stderr)
            return jsonify({"success": False, "error": error_msg}), 500
        finally:
            # Clean up the uploaded file
            if 'image_path' in locals() and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    print(f"Cleaned up image: {image_path}", file=sys.stderr)
                except Exception as e:
                    print(f"Error cleaning up image {image_path}: {e}", file=sys.stderr)

    return jsonify({"success": False, "error": "File processing failed"}), 500


@app.route('/api/fishy', methods=['POST'])
def get_fish_info():
    """Endpoint to get local fish information."""
    data = request.json
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    args = []
    # fishy.py currently doesn't take args, it uses hardcoded example coords.
    # We *could* modify fishy.py to accept args, or just run it as is for now.
    # Let's run it as is for simplicity first. If coords are needed, we'll modify fishy.py later.
    # if latitude and longitude:
    #     try:
    #         args.extend([str(float(latitude)), str(float(longitude))])
    #     except ValueError:
    #         return jsonify({"success": False, "error": "Invalid latitude or longitude"}), 400

    result = run_script('fishy.py', args)

    # fishy.py prints lines like "1. Fish Name". We need to parse this.
    if result["success"] and result["output"]:
        try:
            lines = result["output"].strip().split('\n')
            # Find the start of the list
            list_start_index = -1
            for i, line in enumerate(lines):
                if line.strip().startswith("1."):
                    list_start_index = i
                    break

            if list_start_index != -1:
                fish_list = [line.split('.', 1)[1].strip() for line in lines[list_start_index:] if '.' in line]
                return jsonify({"success": True, "data": {"fish": fish_list}})
            elif "No fish data available" in result["output"]:
                 return jsonify({"success": True, "data": {"fish": [], "message": "No fish data available for the area."}})
            else:
                 # If output format is unexpected, return raw output
                 return jsonify({"success": True, "data": {"raw_output": result["output"], "message": "Could not parse fish list from output."}})

        except Exception as e:
            error_msg = f"Error parsing fishy.py output: {e}\nOutput:\n{result['output']}"
            print(error_msg, file=sys.stderr)
            return jsonify({"success": False, "error": error_msg}), 500
    elif not result["success"]:
        return jsonify({"success": False, "error": result["error"]}), 500
    else:
        return jsonify({"success": False, "error": "fishy.py ran successfully but produced no output."}), 500


@app.route('/api/astronomy', methods=['POST'])
def get_astronomy_info():
    """Endpoint to get astronomy information (star chart image URL)."""
    # Get credentials loaded from .env file
    app_id = os.getenv('APP_ID')
    app_secret = os.getenv('APP_SECRET')
    ipinfo_key = os.getenv('API_KEY') # Key for ipinfo.io

    if not app_id or not app_secret:
         return jsonify({"success": False, "error": "Astronomy API credentials (APP_ID, APP_SECRET) not configured on server."}), 500
    # Note: ipinfo_key is optional in astronomy_api.py, but we need location.
    # If key is missing, we'll try to use default coords below.

    # Attempt to get client's IP address
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    # Handle potential multiple IPs in X-Forwarded-For
    if ip_address and ',' in ip_address:
        ip_address = ip_address.split(',')[0].strip()

    location_data = None
    # Handle localhost IPs for testing (ipinfo won't work) or missing ipinfo key
    if ip_address in ('127.0.0.1', '::1') or not ipinfo_key:
        if not ipinfo_key:
             print("Warning: IPInfo API Key (API_KEY) not configured. Using default coordinates for astronomy.", file=sys.stderr)
        else:
             print("Detected localhost IP, using default coordinates for astronomy.", file=sys.stderr)
        # Use default coordinates (e.g., Washington D.C.)
        location_data = {"latitude": 38.8951, "longitude": -77.0364}
    else:
        location_data = get_location_from_ip(ip_address, ipinfo_key)

    if not location_data or "latitude" not in location_data or "longitude" not in location_data:
        error_msg = location_data.get("error", "Could not determine location from IP address.") if location_data else "Could not determine location from IP address."
        return jsonify({"success": False, "error": error_msg}), 500

    # Call the refactored function to get the star chart URL
    result = get_star_chart_image_url(
        latitude=location_data["latitude"],
        longitude=location_data["longitude"],
        app_id=app_id,
        app_secret=app_secret
    )

    if result.get("success"):
        # Instead of raw output, return the image URL
        return jsonify({"success": True, "data": {"image_url": result["image_url"]}})
    else:
        error_msg = result.get("error", "Failed to generate star chart.")
        details = result.get("details")
        print(f"Astronomy API Error: {error_msg} Details: {details}", file=sys.stderr)
        return jsonify({"success": False, "error": error_msg, "details": details}), 500


# --- Main Execution ---
if __name__ == '__main__':
    # Note: debug=True is helpful for development but should be False in production
    app.run(debug=True, port=5001) # Using port 5001 to avoid potential conflicts