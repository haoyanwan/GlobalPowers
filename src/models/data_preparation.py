import pymongo

# Establish connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["test"]  # Replace with your DB name
game_collection = db["game_files"]
player_collection = db["players"]


def process_game(game):
    # create a temp json in memory
    players = []
    player = {"events": [], "id": "", "tournament_name": ""}


# Extract features and labels from your loaded player_data
def extract_features(game_event):
    # Extract features
    features = [
        game_event.get("Game Time", 0),
        game_event.get("Kills", 0),
        game_event.get("Deaths", 0),
        game_event.get("Assists", 0),
        game_event.get("Kill Participation", 0),
        game_event.get("CS per Minute", 0),
        game_event.get("Gold per Minute", 0),
        game_event.get("Damage Dealt to Champions", 0),
        game_event.get("Damage Taken", 0),
        game_event.get("Crowd Control Score", 0),
        game_event.get("Wards Placed", 0),
        game_event.get("Wards Killed", 0),
        game_event.get("Vision Score", 0),
        game_event.get("teamID", 0),
    ]
    # Convert boolean win value to integer (1 for True, 0 for False)
    label = 1 if game_event.get("win", False) else 0

    return features, label


for game in game_collection.find({}):
    players = []
    game_events = game.get("events", [])
    for game_event in game_events:
        if game_event.get("eventType") == "game_info":
            # Extract the list of player names
            player_names = [participant['summonerName'].strip() for participant in game_event['participants']]
            words = player_names[0].split()
            if len(words) == 2:
                name = words[1]
            else:
                name = words[-1]  # return the original name if it's not two words

            # Query the database for the player IDs
            try:
                player_ids = [player['player_id'] for player in player_collection.find({'handle':  name})]
            except KeyError:
                print("KeyError")
                continue

            # If the player is not found, skip this game
            for id in player_ids:
                if id is None:
                    print("None")
                    continue
                else:
                    platformGameID_to_check = game_event.get("platformGameId")  # replace with your actual platformGameID
                    game = [platformGameID_to_check]
                    for event in game_events:
                        if event.get("eventType") == "stats_update" or event.get("eventType") == "game_info":
                            game.append(event)
                        if event.get("gameOver"):
                            game.append(event)

                    player_collection.update_one({'player_id': id}, {'$set': {'games': game}})




