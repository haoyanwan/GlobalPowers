import json
import os


# loads the game data
def load_game_data(json_file_path):
    try:
        with open(json_file_path, "r") as json_file:
            game_data = json.load(json_file)
        return game_data
    except FileNotFoundError:
        print(f"The game file '{json_file_path}' does not exist.")
        return None


# Function to remove team tags from summoner names
def remove_team_tags(summoner_name):
    # Assuming team tags are uppercase and followed by a space
    return " ".join(summoner_name.split()[1:]) if summoner_name else ""


def main():
    # Specify the directory containing your JSON files
    directory_path = "../../games_data"

    # List of game file paths to process
    game_file_paths = [
    ]

    # Iterate through each game file and store the file paths in a list
    for root, _, files in os.walk(directory_path):
        for filename in files:
            if filename.endswith(".json"):
                file_path = os.path.join(root, filename)
                game_file_paths.append(file_path)

    # Specify the directory containing your player JSON
    player_file_path = "../../esports-data/players.json"
    with open(player_file_path, "r", encoding="utf-8") as players_file:
        players_data = json.load(players_file)

    # Create a dictionary to store player counts
    player_counts = {player["handle"]: 0 for player in players_data}
    games_processed = 0
    for i, game_file_path in enumerate(game_file_paths, start=1):
        with open(game_file_path, "r") as json_file:
            game_data = json.load(json_file)

            # Initialization
            player_stats = {}
            for i in range(1, 11):  # Assuming 10 players with IDs from 1 to 10
                player_stats[i] = [{
                        "Name": "",
                        "Champion Played": "",
                        "Lane": 0,  # 1 top, 2 jg, 3 mid, 4 bot, 5 sup
                        "Version": "",
                        "Kills": 0,
                        "Deaths": 0,
                        "Assists": 0,
                        "CS": 0,
                        "Gold": 0,
                        "Damage Dealt to Champions": 0,
                        "Damage Taken": 0,
                        "Healing Done": 0,
                        "Crowd Control Score": 0,
                        "NEUTRAL_MINIONS_KILLED_YOUR_JUNGLE": 0,
                        "NEUTRAL_MINIONS_KILLED_ENEMY_JUNGLE": 0,
                        "Wards Placed": 0,
                        "Wards Killed": 0,
                        "Vision Score": 0,
                        "TeamID": 0,
                        "Win": "",
                        "Time": "",
                        "Team_100": "",
                        "Team_200": "",
                        "Game Time": 0,
                }]
            count = 0
            event_count = 0
            # Process each event
            for event in game_data:
                event_type = event["eventType"]

                # this processes all game info events
                if event_type == "game_info":

                    game_id = event["platformGameId"]

                    team_100 = [player["summonerName"] for player in event["participants"] if player["teamID"] == 100]
                    team_200 = [player["summonerName"] for player in event["participants"] if player["teamID"] == 200]

                    for i in range(1, 11):  # Assuming player IDs are from 1 to 10

                        player = event["participants"][i - 1]
                        #print(f"i - 1: {i - 1} i - 1 + 5 % 10: {(i - 1 + 5) % 10}")
                        lane_oponent = event["participants"][(i - 1 + 5) % 10]

                        player_stats[i][0]["Lane"] = i % 5
                        player_stats[i][0]["Name"] = player["summonerName"]
                        player_stats[i][0]["Champion Played"] = player["championName"]
                        player_stats[i][0]["Version"] = event["gameVersion"]
                        player_stats[i][0]["TeamID"] = player['teamID']
                        player_stats[i][0]["Time"] = event["eventTime"]
                        player_stats[i][0]["Team_100"] = team_100
                        player_stats[i][0]["Team_200"] = team_200

                        player_stats[i][0]["Lane Opponent"] = lane_oponent["summonerName"]
                        player_stats[i][0]["Champion Played Opponent"] = lane_oponent["championName"]
                        player_stats[i][0]["Version Opponent"] = event["gameVersion"]
                        player_stats[i][0]["TeamID Opponent"] = lane_oponent['teamID']
                        player_stats[i][0]["Time Opponent"] = event["eventTime"]
                        player_stats[i][0]["Team_100 Opponent"] = team_100
                        player_stats[i][0]["Team_200 Opponent"] = team_200

                # this processes all game end events
                elif event_type == "game_end":
                    for j in range(1, 11):
                        player_stats[j][0]["Win"] = event["winningTeam"] == player_stats[j][0]["TeamID"]


                # this processes all stats update events
                elif event_type == "stats_update":  # If the game is over
                    count += 1
                    if count % 60 == 0:
                        event_count += 1
                        # Extract gameTime for CS per Minute and Gold per Minute calculations
                        gameTime = event["gameTime"]

                        # Loop through each participant to extract and update stats
                        for participant_data in event["participants"]:
                            participantID = participant_data["participantID"]

                            opponentID = (participantID + 5) % 10

                            # Create a dictionary for each participant if they don't exist
                            if participantID not in player_stats:
                                player_stats[participantID] = [{}]

                            #print(event_count)
                            if len(player_stats[participantID]) - 1 <= event_count:
                                #print("appending")
                                player_stats[participantID].append({})
                                #print(player_stats[participantID])
                            # Extracting stats from the stats array using list comprehension and dict comprehension
                            stats_dict = {stat["name"]: stat["value"] for stat in participant_data["stats"]}
                            player_stats[participantID][event_count]["Kills"] = stats_dict.get("CHAMPIONS_KILLED", 0)
                            player_stats[participantID][event_count]["Deaths"] = stats_dict.get("NUM_DEATHS", 0)
                            player_stats[participantID][event_count]["Assists"] = stats_dict.get("ASSISTS", 0)
                            player_stats[participantID][event_count]["Game Time"] = gameTime
                            player_stats[participantID][event_count]["CS"] = stats_dict.get("MINIONS_KILLED", 0)
                            player_stats[participantID][event_count]["Gold"] = participant_data["totalGold"]
                            player_stats[participantID][event_count]["Damage Dealt to Champions"] = stats_dict.get(
                                "TOTAL_DAMAGE_DEALT_TO_CHAMPIONS", 0)
                            player_stats[participantID][event_count]["Damage Taken"] = stats_dict.get("TOTAL_DAMAGE_TAKEN", 0)
                            player_stats[participantID][event_count]["Total Heal"] = stats_dict.get("TOTAL_HEAL", 0)  # You may need to adjust the key based on the actual event data
                            player_stats[participantID][event_count]["Crowd Control Score"] = stats_dict.get("TOTAL_TIME_CROWD_CONTROL_DEALT", 0)
                            player_stats[participantID][event_count]["NEUTRAL_MINIONS_KILLED_YOUR_JUNGLE"] = stats_dict.get("NEUTRAL_MINIONS_KILLED_YOUR_JUNGLE", 0)
                            player_stats[participantID][event_count]["NEUTRAL_MINIONS_KILLED_ENEMY_JUNGLE"] = stats_dict.get("NEUTRAL_MINIONS_KILLED_ENEMY_JUNGLE", 0)
                            player_stats[participantID][event_count]["Wards Placed"] = stats_dict.get("WARD_PLACED", 0)
                            player_stats[participantID][event_count]["Wards Killed"] = stats_dict.get("WARD_KILLED", 0)
                            player_stats[participantID][event_count]["Vision Score"] = stats_dict.get("VISION_SCORE", 0)

                            #print(f"opponentID: {opponentID}")
                            opponent_stats_dict = {stat["name"]: stat["value"] for stat in event["participants"][opponentID-1]["stats"]}
                            player_stats[participantID][event_count]["Kills Opponent"] = opponent_stats_dict.get("CHAMPIONS_KILLED", 0)
                            player_stats[participantID][event_count]["Deaths Opponent"] = opponent_stats_dict.get("NUM_DEATHS", 0)
                            player_stats[participantID][event_count]["Assists Opponent"] = opponent_stats_dict.get("ASSISTS", 0)
                            player_stats[participantID][event_count]["Game Time Opponent"] = gameTime
                            player_stats[participantID][event_count]["CS Opponent"] = opponent_stats_dict.get("MINIONS_KILLED", 0)
                            player_stats[participantID][event_count]["Gold Opponent"] = event["participants"][opponentID-1]["totalGold"]
                            player_stats[participantID][event_count]["Damage Dealt to Champions Opponent"] = opponent_stats_dict.get(
                                "TOTAL_DAMAGE_DEALT_TO_CHAMPIONS", 0)
                            player_stats[participantID][event_count]["Damage Taken Opponent"] = opponent_stats_dict.get("TOTAL_DAMAGE_TAKEN", 0)
                            player_stats[participantID][event_count]["Total Heal Opponent"] = opponent_stats_dict.get("TOTAL_HEAL", 0)  # You may need to adjust the key based on the actual event data
                            player_stats[participantID][event_count]["Crowd Control Score Opponent"] = opponent_stats_dict.get("TOTAL_TIME_CROWD_CONTROL_DEALT", 0)
                            player_stats[participantID][event_count]["NEUTRAL_MINIONS_KILLED_YOUR_JUNGLE Opponent"] = opponent_stats_dict.get("NEUTRAL_MINIONS_KILLED_YOUR_JUNGLE", 0)
                            player_stats[participantID][event_count]["NEUTRAL_MINIONS_KILLED_ENEMY_JUNGLE Opponent"] = opponent_stats_dict.get("NEUTRAL_MINIONS_KILLED_ENEMY_JUNGLE", 0)
                            player_stats[participantID][event_count]["Wards Placed Opponent"] = opponent_stats_dict.get("WARD_PLACED", 0)
                            player_stats[participantID][event_count]["Wards Killed Opponent"] = opponent_stats_dict.get("WARD_KILLED", 0)
                            player_stats[participantID][event_count]["Vision Score Opponent"] = opponent_stats_dict.get("VISION_SCORE", 0)


            # Print or store the data as desired
            #print(player_stats)

            # After processing all the events, stores in files
            for pid, stats in player_stats.items():
                # Create a directory for the player if it doesn't exist
                player_directory = os.path.join("players_data", stats[0]["Name"].strip())
                os.makedirs(player_directory, exist_ok=True)

                # player_file_path = os.path.join(player_directory, f"{stats['Name']}.json")
                player_file_path = os.path.join(player_directory, f"{stats[0]['Name'].strip()}.json")

                # If the file already exists, load its contents and append the new game data if it's not a duplicate
                if os.path.exists(player_file_path):
                    with open(player_file_path, "r") as file:
                        existing_data = json.load(file)

                        # check if player has any games_data
                        if "games_data" not in existing_data:
                            existing_data["games_data"] = []
                            #print(f"Player {stats[0]['Name']} has no games_data")

                        # Check if the game is already saved
                        game_already_saved = any(
                            game[0].get('gameId', None) == game_id for game in existing_data["games_data"])
                        #print(f"Game already saved: {game_already_saved}")
                        if not game_already_saved:
                            stats[0]["gameId"] = game_id
                            existing_data["games_data"].append(stats)
                            #print(f"{stats[0]['Name']} game saved")

                    with open(player_file_path, "w") as file:
                        json.dump(existing_data, file, indent=4)
                        games_processed += 1
                        #print(f"Game saved for {stats[0]['Name']}")
                else:
                    # If the file doesn't exist, create it and add the game data
                    stats[0]["gameId"] = game_id
                    with open(player_file_path, "w") as file:
                        json.dump({"games_data": [stats]}, file, indent=4)
                        games_processed += 1
                        #print(f"Game saved for {stats[0]['Name']}")

            # Print player counts every 20 games_data processed
            if games_processed % 20 == 0:
                sorted_counts = sorted(player_counts.items(), key=lambda x: x[1], reverse=True)
                sorted_counts = sorted_counts[:40]

                print(f"Processed {games_processed} games_data")


if __name__ == "__main__":
    main()
