// Store team names
let blueTeamName = "Blue Team";
let redTeamName = "Red Team";

function updateTeamNames() {
    document.getElementById('blue-team-display').textContent = blueTeamName;
    document.getElementById('red-team-display').textContent = redTeamName;
}

// Handle team name input changes
document.getElementById('blue-team-name').addEventListener('input', function(e) {
    blueTeamName = e.target.value || "Blue Team";
    updateTeamNames();
});

document.getElementById('red-team-name').addEventListener('input', function(e) {
    redTeamName = e.target.value || "Red Team";
    updateTeamNames();
});

function updateOverlay(data) {
    const sections = ['blue_team_picks', 'blue_team_bans', 'red_team_picks', 'red_team_bans'];
    const containers = {
        'blue_team_picks': document.getElementById('blue-picks'),
        'blue_team_bans': document.getElementById('blue-bans'),
        'red_team_picks': document.getElementById('red-picks'),
        'red_team_bans': document.getElementById('red-bans')
    };

    sections.forEach(section => {
        const container = containers[section];
        container.innerHTML = '';

        if (data[section]) {
            data[section].forEach(championId => {
                const champDiv = document.createElement('div');
                champDiv.className = 'champion-item';
                champDiv.textContent = `Champion ${championId}`;
                container.appendChild(champDiv);
            });
        }
    });

    // Ensure team names persist after data updates
    updateTeamNames();
}

function fetchGameData() {
    fetch('/api/game-data')
        .then(response => response.json())
        .then(result => {
            if (result.status === 'success') {
                updateOverlay(result.data);
                document.querySelector('.error-message')?.remove();
            } else if (result.status === 'no_game') {
                console.log('No active game found');
            } else {
                throw new Error(result.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.textContent = `Error: ${error.message}`;
            document.body.prepend(errorDiv);
        });
}

// Update data every 10 seconds
setInterval(fetchGameData, 10000);

// Initial fetch
fetchGameData();