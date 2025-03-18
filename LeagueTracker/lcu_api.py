import os
import requests
import json
import urllib3
import base64
import psutil
import re
import logging
from typing import Optional, Dict, Any

# Disable insecure HTTPS warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

# Enable detailed debug mode if environment variable is set
DEBUG_MODE = os.environ.get('LOL_OVERLAY_DEBUG', '0') == '1'

class LCUApi:
    def __init__(self):
        self.auth_token = None
        self.port = None
        self.process = None
        self.session = requests.Session()
        self.session.verify = False

    def get_client_info(self) -> bool:
        """Get League Client info from running process"""
        try:
            logger.info("Starting League client process search...")

            if DEBUG_MODE:
                logger.info("\n=== DEBUG MODE: Searching for League Client ===")
                try:
                    import ctypes
                    is_admin = ctypes.windll.shell32.IsUserAnAdmin() if os.name == 'nt' else os.geteuid() == 0
                    logger.info(f"Running with admin privileges: {is_admin}")
                except Exception as e:
                    logger.info(f"Could not determine admin status: {e}")

                logger.info("Current running processes:")
                for proc in psutil.process_iter(['name', 'cmdline', 'pid']):
                    try:
                        proc_info = proc.as_dict(attrs=['name', 'cmdline', 'pid'])
                        logger.info(f"PID: {proc_info['pid']} | Name: {proc_info['name']}")
                        if proc_info['cmdline']:
                            logger.info(f"Command line: {' '.join(proc_info['cmdline'])}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                        logger.debug(f"Could not access process {proc}: {str(e)}")
                logger.info("=== End of process list ===\n")

            # Different possible names for the League client process
            league_processes = [
                'LeagueClientUx.exe',
                'LeagueClientUx',
                'LeagueClient.exe',
                'LeagueClient',
                'RiotClientUx.exe',
                'RiotClientUx',
                'League of Legends.exe',
                'League of Legends'
            ]

            for proc in psutil.process_iter(['name', 'cmdline']):
                try:
                    proc_info = proc.as_dict(attrs=['name', 'cmdline'])
                    proc_name = proc_info['name']
                    cmdline = proc_info['cmdline']

                    if not proc_name or not cmdline:
                        continue

                    if any(proc_name.lower().startswith(name.lower()) for name in league_processes):
                        logger.info(f"Found potential League client process: {proc_name}")
                        cmdline_str = ' '.join(cmdline)

                        if DEBUG_MODE:
                            logger.info(f"Full command line for {proc_name}: {cmdline_str}")

                        # More flexible pattern matching for the parameters
                        port_matches = re.findall(r"--app-port[=\s](\d+)", cmdline_str)
                        auth_matches = re.findall(r"--remoting-auth-token[=\s]([\w-]+)", cmdline_str)

                        if port_matches and auth_matches:
                            self.port = port_matches[0]
                            self.auth_token = auth_matches[0]
                            self.process = proc
                            logger.info(f"Successfully connected to League client on port {self.port}")

                            if DEBUG_MODE:
                                logger.info("Test connection to client...")
                                test_url = f'https://127.0.0.1:{self.port}/riotclient/app-port'
                                auth = base64.b64encode(f'riot:{self.auth_token}'.encode('utf-8')).decode('utf-8')
                                try:
                                    response = self.session.get(
                                        test_url, 
                                        headers={'Authorization': f'Basic {auth}'},
                                        timeout=3
                                    )
                                    logger.info(f"Test connection response: {response.status_code}")
                                except Exception as e:
                                    logger.warning(f"Test connection failed: {str(e)}")

                            return True
                        else:
                            if DEBUG_MODE:
                                logger.info(f"Required parameters not found in command line for {proc_name}")
                                logger.info(f"Looking for: --app-port and --remoting-auth-token")

                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                    if DEBUG_MODE:
                        logger.warning(f"Error accessing process: {str(e)}")
                    continue

            logger.warning("No League client process found with required parameters")
            return False

        except Exception as e:
            logger.error(f"Error during League client search: {str(e)}", exc_info=True if DEBUG_MODE else False)
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
            if DEBUG_MODE:
                logger.info(f"Making request to: {url}")

            response = self.session.request(method, url, headers=headers, timeout=3)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to League Client: {str(e)}")
            if DEBUG_MODE:
                logger.error("Full error details:", exc_info=True)
            return None

    def get_champ_select(self) -> Optional[Dict[str, Any]]:
        """Get current champion select session"""
        return self.make_request('/lol-champ-select/v1/session')

    def get_picks_and_bans(self) -> Dict[str, list]:
        """Extract picks and bans from current champion select"""
        try:
            session = self.get_champ_select()
            if not session:
                logger.info("No active champion select session found")
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
            bans = session.get('bans', {})
            if bans:
                for ban in bans.get('myTeamBans', []):
                    if ban != 0:  # 0 means no ban
                        picks_and_bans['blue_team_bans'].append(ban)
                for ban in bans.get('theirTeamBans', []):
                    if ban != 0:
                        picks_and_bans['red_team_bans'].append(ban)

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

            if DEBUG_MODE:
                logger.info(f"Processed picks and bans: {picks_and_bans}")
            return picks_and_bans

        except Exception as e:
            logger.error(f"Error processing picks and bans: {str(e)}")
            if DEBUG_MODE:
                logger.error("Full error details:", exc_info=True)
            return picks_and_bans