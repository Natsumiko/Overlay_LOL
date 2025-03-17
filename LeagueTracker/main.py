import os
from flask import Flask, render_template, jsonify
import logging
from lcu_api import LCUApi

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")

# Initialize LCU API
lcu_api = LCUApi()

@app.route('/')
def overlay():
    return render_template('overlay.html')

@app.route('/api/game-data')
def game_data():
    try:
        picks_and_bans = lcu_api.get_picks_and_bans()
        if picks_and_bans:
            return jsonify({
                'status': 'success',
                'data': picks_and_bans
            })
        return jsonify({
            'status': 'no_game',
            'message': 'No champion select session found'
        })
    except Exception as e:
        logger.error(f"Error fetching game data: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)