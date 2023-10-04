import os

import pymongo
import json
import time
# Establish connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["test"]  # Replace with your DB name
collection = db["players"]

'''file = open("../esports-data/players.json", "r", encoding="utf-8")
player_data = json.load(file)
file = open("../esports-data/leagues.json", "r", encoding="utf-8")
leagues = json.load(file)
file = open("../esports-data/tournaments.json", "r", encoding="utf-8")
tournaments = json.load(file)

# Check for empty values and throw errors
for record in player_data:
    for key, value in record.items():
        if not value and key != "home_team_id":  # It's okay for home_team_id to be null, but not other fields
            raise ValueError(f"Empty value detected for {key} in record {record['player_id']}")

# Insert data, skipping any duplicates
for record in player_data:
    if not collection.find_one({"player_id": record["player_id"]}):
        try:
            collection.insert_one(record)
        except pymongo.errors.DuplicateKeyError:
            # This can be reached if there's a unique index constraint
            # (though you mentioned there's no need to create a unique index)
            print(f"Duplicate player detected: {record['player_id']}")
    else:
        print(f"Duplicate player detected: {record['player_id']}")

# 1. Establish connection
collection = db["tournaments"]

# 2. Load the tournaments and leagues data & 3. Check the tournaments against the leagues data
all_tournament_ids = {tournament['id'] for tournament in tournaments}

league_tournament_ids = set()
for league in leagues:
    for tournament in league['tournaments']:
        league_tournament_ids.add(tournament['id'])

valid_tournaments = [tournament for tournament in tournaments if tournament['id'] in league_tournament_ids]

# 4. Insert valid tournaments into the MongoDB collection
for tournament in valid_tournaments:
    # Find the league name for this tournament
    for league in leagues:
        if any(t['id'] == tournament['id'] for t in league['tournaments']):
            tournament['league_name'] = league['name']
            break

    # Insert the tournament ensuring uniqueness using the tournament's id
    try:
        collection.update_one({'id': tournament['id']}, {"$set": tournament}, upsert=True)
    except pymongo.errors.DuplicateKeyError:
        print(f"Duplicate tournament detected (ID: {tournament['id']}). Skipping...")

print("Insertion complete.")

games_collection = db["completed_games"]  # This is the collection where completed games_data will be stored

# Query all tournaments
tournaments = collection.find({})

# Iterate through each tournament, then each stage, each section, and each match to extract game IDs
game_ids = []

# Count the games_data that were not completed
not_completed_count = 0
what = ""
for tournament in tournaments:
    tournament_name = tournament.get('slug')

    for stage in tournament.get('stages', []):
        for section in stage.get('sections', []):
            for match in section.get('matches', []):
                for game in match.get('games_data', []):
                    if game.get('state') == "completed":
                        game['tournament_name'] = tournament_name  # Attach the tournament name to the game
                        game['tournament_id'] = tournament['id']
                        # Insert the game ensuring uniqueness using the game's id
                        try:
                            games_collection.update_one({'id': game['id']}, {"$set": game}, upsert=True)
                        except pymongo.errors.DuplicateKeyError:
                            print(f"Duplicate game detected (ID: {game['id']}). Skipping...")

                        what = game.get('state')
                        not_completed_count += 1
                    game_id = game.get('id')
                    if game_id:
                        game_ids.append(game_id)
# Print all the extracted game IDs
for game_id in game_ids:
    print(game_id)

# The JSON data
data = json.load(open("../esports-data/mapping_data.json", "r", encoding="utf-8"))

# Directory containing the nested folders with game files


# Extract platformGameId values and convert them to expected filename format
expected_files = [entry['platformGameId'].replace(':', '_') + '.json' for entry in data]


'''
collection = db["game_files"]
data = json.load(open("../esports-data/mapping_data.json", "r", encoding="utf-8"))
completed_games_collection = db["completed_games"]
root_directory = "../games_data"  # Replace this with the path to your directory
expected_files = [entry['platformGameId'].replace(':', '_') + '.json' for entry in data]


def get_tournament_name(game_id):
    games = completed_games_collection.find({})
    for entry in games:
        if entry['id'] == game_id:
            return entry['tournament_name']


def process_game_file(filepath):
    # create a temp json in memory
    temp = {"events": [], "id": "", "tournament_name": ""}
    game_events = json.load(open(filepath, "r", encoding="utf-8"))
    second = 0
    gameEnd = False
    for event in game_events:
        if event.get("eventType") != "stats_update":
            gameEnd = event.get("gameOver")
            temp.get("events").append(event)
        else:
            second += 1
            if second % 60 == 0:
                temp.get("events").append(event)
            if gameEnd:
                print("game end")
                temp.get("events").append(event)

    return temp


game_files_collection = db["game_files"]
game_files = game_files_collection.find({})
count = 0
# Traverse the directory to find and read the matching game files
for subdir, _, files in os.walk(root_directory):
    for i, file in enumerate(files):
        if file in expected_files:
            filepath = os.path.join(subdir, file)
            filepath = filepath[-26:-5].replace("_", ":")  # Remove the "../games_data" prefix

            times = time.time()

            for entry in data:
                if entry['platformGameId'] == filepath:
                    esports_game_id = entry['esportsGameId']
                    print(f"Found matching game file: {filepath} (esportsGameId: {esports_game_id})")
                    print(f"Finding matching game file took: {time.time() - times}")
                    times = time.time()
                    # Check if the specific ID exists in the collection

                    result = game_files_collection.find_one({'id': esports_game_id}, {'_id': 1}) is not None
                    print(f"Finding matching game file from collection took: {time.time() - times}")
                    times = time.time()

                    if result:
                        count = count + 1
                        if count % 10 == 0:
                            print(f"count: {count} Game file with ID {esports_game_id} already exists. Skipping...")
                        break
                    jsons = process_game_file(os.path.join(subdir, file))
                    print(f"Processing game file took: {time.time() - times}")
                    times = time.time()
                    jsons["id"] = esports_game_id
                    jsons["tournament_name"] = get_tournament_name(esports_game_id)
                    collection.update_one({"id": esports_game_id}, {"$set": jsons}, upsert=True)
                    print(f"Inserting game file took: {time.time() - times}")
                    times = time.time()
                    print(f"Processing file {i + 1} of {len(files)}: {filepath}")


print("Insertion of matching game files complete.")

client.close()
