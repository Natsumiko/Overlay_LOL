# League of Legends Pick/Ban Overlay

A web-based application for manually creating League of Legends champion pick and ban overlays for streaming purposes, allowing real-time input and display of team compositions.

## Features

- Manual input of champion picks and bans
- Real-time updates to the overlay
- Customizable team names
- Streaming-friendly overlay interface
- Dark theme optimized for streaming

## Project Structure

```
├── main.py                 # Flask application entry point
├── templates/
│   ├── control.html       # Control panel for manual input
│   └── overlay.html       # OBS overlay display
└── static/
    └── css/
        └── style.css      # Styling for the overlay
```

## Requirements

- Python 3.11 or higher
- The following Python packages:
  - flask
  - gunicorn

## Running the Application

1. Start the Flask application:
```bash
python main.py
```

2. Access the application:
- Control Panel: http://127.0.0.1:5000/control
  - Use this to input team names and champions
- Overlay URL: http://127.0.0.1:5000
  - Add this URL to OBS as a Browser Source

## Using the Overlay

1. Open the Control Panel in your browser
2. Input team names for both sides
3. Add champion picks and bans as they happen
4. The overlay will update in real-time

## Setting up in OBS

1. Add a new "Browser" source in OBS
2. Set the URL to: http://127.0.0.1:5000
3. Set the width and height as needed for your overlay
4. (Optional) Add custom CSS if you want to make the background transparent

## Features

- Real-time manual input for picks and bans
- Customizable team names
- Dark theme optimized for streaming
- Transparent background support for OBS
- Reset button to clear all picks and bans