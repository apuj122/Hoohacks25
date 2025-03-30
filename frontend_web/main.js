// --- Plan Trip Page Logic ---
const planTripForm = document.getElementById('plan-trip-form');
const mapContainer = document.getElementById('map-container');
const mapIframe = document.getElementById('map-iframe');
const statusMessage = document.getElementById('status-message'); // Common status element

if (planTripForm) {
    planTripForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default page reload

        // Clear previous status and hide map
        if (statusMessage) statusMessage.textContent = '';
        if (mapContainer) mapContainer.style.display = 'none';
        if (mapIframe) mapIframe.src = 'about:blank'; // Clear previous map

        // Show loading message
        if (statusMessage) {
            statusMessage.textContent = 'Generating adventure map... Please wait.';
            statusMessage.className = ''; // Reset classes
        }

        const latitude = document.getElementById('latitude').value;
        const longitude = document.getElementById('longitude').value;
        const radius = document.getElementById('radius').value;

        try {
            const response = await fetch('/api/plan_trip', { // Assuming backend runs on the same origin or proxied
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    latitude: latitude,
                    longitude: longitude,
                    radius_miles: radius
                }),
            });

            const result = await response.json();

            if (response.ok && result.success && result.map_url) {
                if (statusMessage) statusMessage.textContent = 'Map generated successfully!';
                if (statusMessage) statusMessage.className = 'success';
                if (mapIframe) {
                    // Add a timestamp to prevent browser caching issues with the iframe source
                    mapIframe.src = result.map_url + '?t=' + new Date().getTime();
                }
                 if (mapContainer) mapContainer.style.display = 'block'; // Show the map container
            } else {
                throw new Error(result.error || 'Failed to generate map. Check backend logs.');
            }
        } catch (error) {
            console.error('Error planning trip:', error);
            if (statusMessage) statusMessage.textContent = `Error: ${error.message}`;
            if (statusMessage) statusMessage.className = 'error';
        }
    });
}

// --- On Trip Page Logic ---
const imageUpload = document.getElementById('image-upload');
const identifyAnimalBtn = document.getElementById('identify-animal-btn');
const identifyBirdBtn = document.getElementById('identify-bird-btn');
const identifyFloraBtn = document.getElementById('identify-flora-btn');
const getFishBtn = document.getElementById('get-fish-btn');
const getAstroBtn = document.getElementById('get-astro-btn');
const resultsDiv = document.getElementById('results');
// Re-use status message element from plan_trip page if available, or assume it exists
const onTripStatusMessage = document.getElementById('status-message');

// Function to handle identification requests
async function handleIdentification(idType) {
    if (!imageUpload || !imageUpload.files || imageUpload.files.length === 0) {
        if (onTripStatusMessage) {
            onTripStatusMessage.textContent = 'Error: Please select an image file first.';
            onTripStatusMessage.className = 'error';
        }
        return;
    }

    const file = imageUpload.files[0];
    const formData = new FormData();
    formData.append('image', file);
    formData.append('id_type', idType); // 'animal', 'bird', or 'flora'

    // Clear previous status/results
    if (onTripStatusMessage) onTripStatusMessage.textContent = '';
    if (resultsDiv) resultsDiv.style.display = 'none';
    if (resultsDiv) resultsDiv.textContent = '';


    if (onTripStatusMessage) {
        onTripStatusMessage.textContent = `Identifying ${idType}... Please wait.`;
        onTripStatusMessage.className = '';
    }

    try {
        const response = await fetch('/api/identify', {
            method: 'POST',
            body: formData, // No 'Content-Type' header needed for FormData, browser sets it
        });

        const result = await response.json();

        if (response.ok && result.success) {
            if (onTripStatusMessage) onTripStatusMessage.textContent = `${idType.charAt(0).toUpperCase() + idType.slice(1)} identified successfully!`;
            if (onTripStatusMessage) onTripStatusMessage.className = 'success';
            if (resultsDiv) {
                // Display formatted JSON results
                resultsDiv.textContent = JSON.stringify(result.data, null, 2); // Pretty print JSON
                resultsDiv.style.display = 'block';
            }
        } else {
            throw new Error(result.error || `Failed to identify ${idType}.`);
        }
    } catch (error) {
        console.error(`Error identifying ${idType}:`, error);
        if (onTripStatusMessage) onTripStatusMessage.textContent = `Error: ${error.message}`;
        if (onTripStatusMessage) onTripStatusMessage.className = 'error';
    }
}

// Add event listeners for identification buttons
if (identifyAnimalBtn) {
    identifyAnimalBtn.addEventListener('click', () => handleIdentification('animal'));
}
if (identifyBirdBtn) {
    identifyBirdBtn.addEventListener('click', () => handleIdentification('bird'));
}
if (identifyFloraBtn) {
    identifyFloraBtn.addEventListener('click', () => handleIdentification('flora'));
}

// Function to handle fishy requests
async function handleFishy() {
    // Clear previous status/results
    if (onTripStatusMessage) onTripStatusMessage.textContent = '';
    if (resultsDiv) resultsDiv.style.display = 'none';
    if (resultsDiv) resultsDiv.textContent = '';

    if (onTripStatusMessage) {
        onTripStatusMessage.textContent = 'Getting local fish info...';
        onTripStatusMessage.className = '';
    }

    // Get optional coordinates (implement getting actual current location later if needed)
    const latitude = document.getElementById('info-latitude')?.value;
    const longitude = document.getElementById('info-longitude')?.value;

    const payload = {};
    if (latitude && longitude) {
        payload.latitude = latitude;
        payload.longitude = longitude;
    }


    try {
        const response = await fetch('/api/fishy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        const result = await response.json();

        if (response.ok && result.success) {
            if (onTripStatusMessage) onTripStatusMessage.textContent = 'Fish info retrieved!';
            if (onTripStatusMessage) onTripStatusMessage.className = 'success';
            if (resultsDiv) {
                // Display formatted results
                let displayText = "Fish Info:\n";
                if (result.data.fish && result.data.fish.length > 0) {
                    result.data.fish.forEach((fish, index) => {
                        displayText += `${index + 1}. ${fish}\n`;
                    });
                } else if (result.data.message) {
                     displayText += result.data.message + "\n";
                } else if (result.data.raw_output) {
                     displayText += "Raw Output:\n" + result.data.raw_output;
                } else {
                    displayText += "No specific fish data found.";
                }
                resultsDiv.textContent = displayText;
                resultsDiv.style.display = 'block';
            }
        } else {
            throw new Error(result.error || 'Failed to get fish info.');
        }
    } catch (error) {
        console.error('Error getting fish info:', error);
        if (onTripStatusMessage) onTripStatusMessage.textContent = `Error: ${error.message}`;
        if (onTripStatusMessage) onTripStatusMessage.className = 'error';
    }
}


// Add event listener for fishy button
if (getFishBtn) {
    getFishBtn.addEventListener('click', handleFishy);
}

// Function to handle astronomy requests
async function handleAstronomy() {
    // Clear previous status/results
    if (onTripStatusMessage) onTripStatusMessage.textContent = '';
    if (resultsDiv) resultsDiv.style.display = 'none';
    if (resultsDiv) resultsDiv.textContent = '';

     if (onTripStatusMessage) {
        onTripStatusMessage.textContent = 'Getting astronomy info...';
        onTripStatusMessage.className = '';
    }

    try {
        // No body needed for this request based on current backend implementation
        const response = await fetch('/api/astronomy', {
            method: 'POST',
             headers: {
                'Content-Type': 'application/json', // Still good practice to send header
            },
            body: JSON.stringify({}), // Send empty JSON object
        });

        const result = await response.json();

        if (response.ok && result.success) {
            if (onTripStatusMessage) onTripStatusMessage.textContent = 'Astronomy info retrieved!';
            if (onTripStatusMessage) onTripStatusMessage.className = 'success';
            if (resultsDiv) {
                // Display raw output
                resultsDiv.textContent = "Astronomy Info:\n" + (result.data.raw_output || "No output received.");
                resultsDiv.style.display = 'block';
            }
        } else {
            throw new Error(result.error || 'Failed to get astronomy info.');
        }
    } catch (error) {
        console.error('Error getting astronomy info:', error);
        if (onTripStatusMessage) onTripStatusMessage.textContent = `Error: ${error.message}`;
        if (onTripStatusMessage) onTripStatusMessage.className = 'error';
    }
}

// Add event listener for astronomy button
if (getAstroBtn) {
    getAstroBtn.addEventListener('click', handleAstronomy);
}