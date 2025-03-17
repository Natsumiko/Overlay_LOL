import os
from flask import Flask, render_template, jsonify
import logging
from lol_api import LoLAPI

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")

# Initialize LoL API
lol_api = LoLAPI(
    api_key=os.environ.get("RIOT_API_KEY", "TO_FILL"),
    encrypted_puuid=os.environ.get("SUMMONER_PUUID", "TO_FILL")
)

@app.route('/')
def overlay():
    return render_template('overlay.html')

@app.route('/api/game-data')
def game_data():
    try:
        game_info = lol_api.get_current_game_info()
        if game_info:
            picks_and_bans = lol_api.get_picks_and_bans(game_info)
            return jsonify({
                'status': 'success',
                'data': picks_and_bans
            })
        return jsonify({
            'status': 'no_game',
            'message': 'No active game found'
        })
    except Exception as e:
        logger.error(f"Error fetching game data: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
