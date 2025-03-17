import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class LoLAPI:
    def __init__(self, api_key: str, encrypted_puuid: str):
        self.api_key = api_key
        self.encrypted_puuid = encrypted_puuid
        self.base_url = 'https://EUW1.api.riotgames.com/lol/spectator/v5/active-games/by-summoner'
        
    def get_current_game_info(self) -> Optional[Dict[str, Any]]:
        """Fetch current game information from Riot API"""
        url = f'{self.base_url}/{self.encrypted_puuid}'
        headers = {"X-Riot-Token": self.api_key}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 404:
                logger.info("No active game found")
                return None
            elif response.status_code != 200:
                error_msg = f"API Error: {response.status_code}, {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise Exception(f"Failed to fetch game data: {str(e)}")

    def get_picks_and_bans(self, game_info: Dict[str, Any]) -> Dict[str, list]:
        """Extract picks and bans from game information"""
        if not game_info:
            return None

        picks_and_bans = {
            'blue_team_bans': [],
            'red_team_bans': [],
            'blue_team_picks': [],
            'red_team_picks': []
        }

        teams = game_info.get('teams', [])
        for team in teams:
            if team['teamId'] == 100:
                picks_and_bans['blue_team_bans'] = [ban['championId'] for ban in team.get('bans', [])]
            else:
                picks_and_bans['red_team_bans'] = [ban['championId'] for ban in team.get('bans', [])]
        
        for participant in game_info.get('participants', []):
            if participant['teamId'] == 100:
                picks_and_bans['blue_team_picks'].append(participant['championId'])
            else:
                picks_and_bans['red_team_picks'].append(participant['championId'])

        return picks_and_bans
