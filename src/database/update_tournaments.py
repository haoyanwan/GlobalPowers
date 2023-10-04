import pymongo
import json

# Establish connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["test"]  # Replace with your DB name
collection = db["tournaments"]


# loads the tournament files from RIOT
league_files = open("../../esports-data/leagues.json", "r", encoding="utf-8")
leagues = json.load(league_files)
tournament_file = open("../../esports-data/tournaments.json", "r", encoding="utf-8")
tournaments = json.load(tournament_file)


# Load the tournaments and leagues data & Check the tournaments against the leagues data
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