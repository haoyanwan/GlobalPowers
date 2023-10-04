import os

import pymongo
import json


# Establish connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["test"]  # Replace with your DB name
collection = db["tournaments"]

games_collection = db["completed_games"]  # This is the collection where completed games_data will be stored

# Query all tournaments
tournaments = collection.find({})

# Iterate through each tournament, then each stage, each section, and each match to extract game IDs
game_ids = []


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

print("Insertion complete.")


