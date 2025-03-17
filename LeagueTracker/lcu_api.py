import os
import requests
import json
import urllib3
import base64
import psutil
import re
from typing import Optional, Dict, Any

# Disable insecure HTTPS warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class LCUApi:
    def __init__(self):
        self.auth_token = None
        self.port = None
        self.process = None
        self.session = requests.Session()
        self.session.verify = False
        
    def get_client_info(self) -> bool:
        """Get League Client info from running process"""
        for proc in psutil.process_iter(['name', 'cmdline']):
            if proc.info['name'] == 'LeagueClientUx.exe':
                cmdline = proc.info['cmdline']
                self.process = proc
                
                # Extract port and auth token from command line
                port_regex = "--app-port=([0-9]*)"
                auth_regex = "--remoting-auth-token=([\w-]*)"
                
                port_match = re.search(port_regex, ' '.join(cmdline))
                auth_match = re.search(auth_regex, ' '.join(cmdline))
                
                if port_match and auth_match:
                    self.port = port_match.group(1)
                    self.auth_token = auth_match.group(1)
                    return True
        return False

    def make_request(self, endpoint: str, method: str = 'GET') -> Optional[Dict[str, Any]]:
        """Make request to League Client API"""
        if not self.auth_token or not self.port:
            if not self.get_client_info():
                return None

        url = f'https://127.0.0.1:{self.port}{endpoint}'
        auth = base64.b64encode(f'riot:{self.auth_token}'.encode('utf-8')).decode('utf-8')
        headers = {
            'Authorization': f'Basic {auth}',
            'Accept': 'application/json'
        }
        
        try:
            response = self.session.request(method, url, headers=headers, timeout=3)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to League Client: {str(e)}")
            return None

    def get_champ_select(self) -> Optional[Dict[str, Any]]:
        """Get current champion select session"""
        return self.make_request('/lol-champ-select/v1/session')

    def get_picks_and_bans(self) -> Dict[str, list]:
        """Extract picks and bans from current champion select"""
        session = self.get_champ_select()
        if not session:
            return {
                'blue_team_bans': [],
                'red_team_bans': [],
                'blue_team_picks': [],
                'red_team_picks': []
            }

        picks_and_bans = {
            'blue_team_bans': [],
            'red_team_bans': [],
            'blue_team_picks': [],
            'red_team_picks': []
        }

        # Process bans
        for team in session.get('bans', {}).get('myTeamBans', []):
            if team != 0:  # 0 means no ban
                picks_and_bans['blue_team_bans'].append(team)
        for team in session.get('bans', {}).get('theirTeamBans', []):
            if team != 0:
                picks_and_bans['red_team_bans'].append(team)

        # Process picks
        for action in session.get('actions', []):
            for pick in action:
                if pick.get('completed', False):
                    champion_id = pick.get('championId', 0)
                    if champion_id != 0:
                        if pick.get('isAllyAction', False):
                            picks_and_bans['blue_team_picks'].append(champion_id)
                        else:
                            picks_and_bans['red_team_picks'].append(champion_id)

        return picks_and_bans
