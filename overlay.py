import requests
import json
import time

API_KEY = 'To_Add'
encryptedPUUID = 'nYrHejZcliiI82HgzVmmOrQCsN1joEkm-v_bOW3mqF0jdpN6-p5OviJnRdLXyN22jZkg5Jy8NCmhhg'
BASE_URL = 'https://EUW1.api.riotgames.com/lol/spectator/v5/active-games/by-summoner'



# Fonction pour obtenir les informations de la partie en cours
def get_current_game_info(encryptedPUUID):
    url = f'{BASE_URL}/{encryptedPUUID}'
    headers = {"X-Riot-Token": API_KEY}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 404:
        print("Aucune partie en cours.")
        return None
    elif response.status_code != 200:
        print(f"Erreur API: {response.status_code}, {response.text}")
        return None
    
    return response.json()

# Fonction pour extraire les picks et bans
def get_picks_and_bans(game_info):
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

# Fonction pour afficher les picks et bans
def update_overlay(picks_and_bans):
    if not picks_and_bans:
        return
    
    print(f"Blue Team Bans: {picks_and_bans['blue_team_bans']}")
    print(f"Red Team Bans: {picks_and_bans['red_team_bans']}")
    print(f"Blue Team Picks: {picks_and_bans['blue_team_picks']}")
    print(f"Red Team Picks: {picks_and_bans['red_team_picks']}")
    print("-" * 50)

# Boucle principale avec backoff exponentiel
wait_time = 10  # Temps initial d'attente

while True:
    game_info = get_current_game_info(encryptedPUUID)
    
    if game_info:
        picks_and_bans = get_picks_and_bans(game_info)
        update_overlay(picks_and_bans)
        wait_time = 10  # Reset du backoff si une partie est trouvée
    else:
        wait_time = min(wait_time * 2, 60)  # Exponential backoff, max 60s
    
    time.sleep(wait_time)
