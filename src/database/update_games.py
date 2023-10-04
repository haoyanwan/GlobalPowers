import os

import pymongo
import json
import time

# Establish connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["test"]  # Replace with your DB name


collection = db["game_files"]
data = json.load(open("../../esports-data/mapping_data.json", "r", encoding="utf-8"))
completed_games_collection = db["completed_games"]
root_directory = "../../games_data"  # Replace this with the path to your directory
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
