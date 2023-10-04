
import pymongo
import json

# Establish connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["test"]  # Replace with your DB name
collection = db["players"]

#load player files from RIOT
file = open("../esports-data/players.json", "r", encoding="utf-8")
player_data = json.load(file)

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