import json
import os

import tensorflow as tf

# Load the saved model
MODEL_SAVE_PATH = "tensorflow_models/1695532743.2426696"
model = tf.keras.models.load_model(MODEL_SAVE_PATH)

# Extract features from a game data
def extract_features(game):
    features = [
        game.get("Kills", 0),
        game.get("Deaths", 0),
        game.get("Assists", 0),
        game.get("Kill Participation", 0),
        game.get("CS per Minute", 0),
        game.get("Gold per Minute", 0),
        game.get("Damage Dealt to Champions", 0),
        game.get("Damage Taken", 0),
        game.get("Crowd Control Score", 0),
        game.get("Wards Placed", 0),
        game.get("Wards Killed", 0),
        game.get("Vision Score", 0),
        game.get("teamID", 0),
    ]
    return features

# Test the model with individual game data
def test_single_game(game):
    # Extract features
    features = extract_features(game)
    prediction = model.predict([features])
    predicted_label = 1 if prediction[0][0] >= 0.5 else 0  # threshold to determine win/lose

    return predicted_label, prediction[0][0]

def main():
    # Here, let's use an example game data. You can replace this with actual data.
    directory_path = "players_data"

    # List of game file paths to process
    player_file_paths = [
    ]

    # Iterate through each game file and store the file paths in a list
    for root, _, files in os.walk(directory_path):
        for filename in files:
            if filename.endswith(".json"):
                file_path = os.path.join(root, filename)
                player_file_paths.append(file_path)


    for filename in player_file_paths:
        with open(filename, "r") as json_file:
            player_data = json.load(json_file)
            for game in player_data["games_data"]:

                predicted_label, win_probability = test_single_game(game)
                #print who won and who is on each team and date and summoner name and champion name
                print(f"Champion Played: {game['Champion Played']}")
                print(f"Summoner Name: {game['Name']}")
                print(f"Team 100: {game['team_100']}")
                print(f"Team 200: {game['team_200']}")
                print(f"Date: {game['time']}")
                print(f"win: {game['win']}")

                if predicted_label == 1:
                    print(f"Predicted to win with a probability of {win_probability*100:.2f}%")
                else:
                    print(f"Predicted to lose with a probability of {(1-win_probability)*100:.2f}%")

                input("Press Enter to continue...")


if __name__ == "__main__":
    main()
