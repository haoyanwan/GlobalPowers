import json
import os
import datetime
import time
from collections import defaultdict

import numpy as np
import tensorflow as tf

print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)


# Extract features and labels from your loaded player_data
def extract_features(game):
    encoder = AutoIncrementEncoder()

    # Extract features
    features = [
        encoder.encode(game.get("Champion Played", "")),
        game.get("Game Time", 0),
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
    # Convert boolean win value to integer (1 for True, 0 for False)
    label = 1 if game.get("win", False) else 0

    return features, label


# Split data into training and testing
def split_data(features, labels, test_size=0.2):
    split_index = int(len(features) * (1 - test_size))
    return features[:split_index], labels[:split_index], features[split_index:], labels[split_index:]


# Define the model architecture
def create_model():
    model = tf.keras.models.Sequential([
        tf.keras.layers.Input(shape=(15,)),  # Input layer (13 features)
        tf.keras.layers.Dense(256, activation='relu'),  # First hidden layer
        tf.keras.layers.Dense(256, activation='relu'),  # Second hidden layer
        tf.keras.layers.Dense(1, activation='sigmoid')  # Output layer (binary classification)
    ])
    return model

# Main training function
def train_model(X_train, y_train):
    model = create_model()

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # Train the model
    model.fit(X_train, y_train, epochs=1000)

    return model


class AutoIncrementEncoder:
    def __init__(self):
        self.encoder = defaultdict(self._auto_increment)
        self.current_int = 0

    def _auto_increment(self):
        current = self.current_int
        self.current_int += 1
        return current

    def encode(self, champion_name):
        return self.encoder[champion_name]

    def encode(self, champion_name):
        return self.encoder[champion_name]


def main():



# Specify the directory containing your JSON files
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


    all_features, all_labels = [], []


    for filename in player_file_paths:
        with open(filename, "r") as json_file:
            player_data = json.load(json_file)

        # Extracting features and labels
            for game in player_data["games_data"]:
                features, label = extract_features(game)
                all_features.append(features)
                all_labels.append(label)

    X_train, y_train, X_test, y_test = split_data(all_features, all_labels)

    #print first 10 features and labels
    print(X_train[:10])
    print(y_train[:10])
    model = train_model(X_train, y_train)


    model.save(f"tensorflow_models/{time.time()}")

    # Evaluate model on test set
    loss, accuracy = model.evaluate(X_test, y_test)
    print(f"Test Accuracy: {accuracy * 100:.2f}%")


if __name__ == "__main__":
    main()