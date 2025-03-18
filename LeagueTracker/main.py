from flask import Flask, render_template, jsonify, request
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")

# Store the current picks and bans in memory
current_state = {
    'blue_team_name': 'Blue Team',
    'red_team_name': 'Red Team',
    'blue_team_picks': [],
    'red_team_picks': [],
    'blue_team_bans': [],
    'red_team_bans': []
}

@app.route('/')
def overlay():
    """Display the overlay view"""
    logger.info("Accessing overlay endpoint")
    return render_template('overlay.html')

@app.route('/control')
def control_panel():
    """Display the control panel for inputting picks and bans"""
    logger.info("Accessing control panel")
    return render_template('control.html')

@app.route('/api/update', methods=['POST'])
def update_data():
    """Update the picks and bans data"""
    try:
        data = request.get_json()
        logger.info(f"Received update request with data: {data}")

        # Update the current state with new data
        if 'team' in data and 'type' in data and 'champion' in data and 'index' in data:
            team_key = f"{data['team']}_team_{data['type']}"
            index = int(data['index'])

            # Ensure the list exists and has enough slots
            while len(current_state[team_key]) <= index:
                current_state[team_key].append('')

            # Update the champion at the specified index
            current_state[team_key][index] = data['champion']

            return jsonify({'status': 'success'})

        # Update team names
        if 'blue_team_name' in data:
            current_state['blue_team_name'] = data['blue_team_name']
        if 'red_team_name' in data:
            current_state['red_team_name'] = data['red_team_name']

        return jsonify({'status': 'success'})

    except Exception as e:
        logger.error(f"Error updating data: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/state')
def get_state():
    """Get the current state of picks and bans"""
    return jsonify(current_state)

@app.route('/reset', methods=['POST'])
def reset_state():
    """Reset all picks and bans"""
    try:
        current_state['blue_team_picks'] = []
        current_state['red_team_picks'] = []
        current_state['blue_team_bans'] = []
        current_state['red_team_bans'] = []
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error resetting state: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    logger.info("Starting Flask application")
    print("\n" + "="*50)
    print("League of Legends Pick/Ban Overlay")
    print("="*50)
    print("\nAccess points:")
    print("1. Overlay (add to OBS):")
    print("   - http://127.0.0.1:5000")
    print("2. Control Panel (for manual input):")
    print("   - http://127.0.0.1:5000/control")
    print("="*50 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)