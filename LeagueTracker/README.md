# League of Legends Pick/Ban Overlay

A Python application that creates an OBS overlay for League of Legends champion picks and bans by connecting to the League Client.

## Project Structure
```
├── main.py                 # Flask application entry point
├── lcu_api.py             # League Client API integration
├── templates/
│   └── overlay.html       # HTML template for the overlay
└── static/
    ├── css/
    │   └── style.css      # Styling for the overlay
    └── js/
        └── update.js      # JavaScript for updating the overlay
```

## Requirements
- Python 3.11 or higher
- League of Legends client installed and running
- The following Python packages:
  - flask
  - psutil
  - requests
  - urllib3

## Local Installation

1. Create a new directory for your project:
```bash
mkdir league-overlay
cd league-overlay
```

2. Create and activate a virtual environment:
```bash
# On Windows:
python -m venv venv
venv\Scripts\activate

# On macOS/Linux:
python -m venv venv
source venv/bin/activate
```

3. Install required packages:
```bash
pip install flask psutil requests urllib3
```

4. Create the following directory structure:
```
league-overlay/
├── main.py
├── lcu_api.py
├── templates/
│   └── overlay.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── update.js
```

5. Copy all the provided files into their respective locations.

## Running the Application

1. Make sure your League of Legends client is running

2. Start the Flask application:
```bash
# On Windows:
python main.py

# On macOS/Linux:
python main.py
```

3. Access the overlay in your web browser:
- URL: http://127.0.0.1:5000
- If that doesn't work, try: http://localhost:5000

## Troubleshooting

If you can't connect to the application:

1. Make sure you're using the correct URL:
   - Try both `http://127.0.0.1:5000` and `http://localhost:5000`
   - If using a different port, adjust the URL accordingly

2. Check if the Flask server is running:
   - Look for the message "Running on http://0.0.0.0:5000"
   - Check for any error messages in the console

3. Verify League Client:
   - Ensure League of Legends client is running
   - The application needs the client running to fetch pick/ban data

4. Common Issues:
   - Port 5000 already in use: Try changing the port in main.py
   - Connection refused: Make sure your firewall isn't blocking the connection
   - No data showing: Verify League client is running and you're in champion select

## Setting up in OBS

1. Add a new "Browser" source in OBS
2. Set the URL to: http://127.0.0.1:5000
3. Set the width and height as needed for your overlay
4. (Optional) Add custom CSS if you want to make the background transparent

## Features

- Real-time picks and bans display
- Customizable team names
- Dark theme optimized for streaming
- Direct connection to League Client (no API key needed)
- Automatic updates during champion select