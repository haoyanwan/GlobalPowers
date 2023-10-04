import os
import json
from validatiing_deep import test_single_game

# Initial setup
directory_path = "players_data"
player_file_paths = []
elo_ratings = {}  # Dictionary to store player elo ratings
BASE_ELO = 1500

# Get the player file paths
for root, _, files in os.walk(directory_path):
    for filename in files:
        if filename.endswith(".json"):
            file_path = os.path.join(root, filename)
            player_file_paths.append(file_path)

# Extract game data from files
all_games = []
for filename in player_file_paths:
    with open(filename, "r") as json_file:
        player_data = json.load(json_file)
        all_games.extend(player_data["games_data"])

# Sort games_data chronologically
all_games.sort(key=lambda x: x["time"])


def update_elo_win(winner_elo, loser_elo, games):
    predicted_label, win_probability = test_single_game(games)
    # ELO calculation formula simplified
    K = 32
    expected_win = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
    new_winner_elo = winner_elo + win_probability * K * (1 - expected_win)
    return new_winner_elo


def update_elo_loss(winner_elo, loser_elo, games):
    predicted_label, win_probability = test_single_game(games)
    # ELO calculation formula simplified
    K = 32
    expected_win = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
    new_loser_elo = loser_elo + (1-win_probability) * K * (0 - expected_win)
    return new_loser_elo


# Loop through sorted games_data and update ELO ratings for the player under "Name"
for game in all_games:
    player_name = game["Name"]
    if player_name not in elo_ratings:
        elo_ratings[player_name] = BASE_ELO

    player_elo = elo_ratings[player_name]
    opponent_team = game["team_100"] if game["teamID"] == 200 else game["team_200"]

    avg_opponent_elo = sum(elo_ratings.get(player, BASE_ELO) for player in opponent_team) / len(opponent_team)

    if game["win"]:
        new_player_elo = update_elo_win(player_elo, avg_opponent_elo, game)
    else:
        new_player_elo = update_elo_loss(avg_opponent_elo, player_elo, game)

    elo_ratings[player_name] = new_player_elo

# Sort elo_ratings by rating and print
sorted_elo_ratings = sorted(elo_ratings.items(), key=lambda x: x[1], reverse=True)

for player, rating in sorted_elo_ratings:
    print(f"{player}: {rating}")
