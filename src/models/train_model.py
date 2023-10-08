import datetime
import json
import os
import time

import numpy as np
from numpy import shape
from sklearn.model_selection import train_test_split

import tensorflow as tf
from tensorflow.python.keras import regularizers

print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

gpus = tf.config.experimental.list_physical_devices('GPU')

if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)


def split_data(features, labels, test_size=0.1):
    split_index = int(len(features) * (1 - test_size))
    return features[:split_index], labels[:split_index], features[split_index:], labels[split_index:]


# Define the model architecture
def create_model():
    model = tf.keras.models.Sequential([
        tf.keras.layers.Input(shape=(13,)),  # Input layer (13 features)
        tf.keras.layers.Dense(64, activation='relu'),  # First hidden layer
        tf.keras.layers.Dropout(0.5),  # Adding dropout after the first hidden layer
        tf.keras.layers.Dense(64, activation='relu', kernel_regularizer=regularizers.l2(0.01)),  # Second hidden layer
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dense(64, activation='relu', kernel_regularizer=regularizers.l2(0.01)),  # Third hidden layer
        tf.keras.layers.Dense(1, activation='sigmoid')  # Output layer (binary classification)
    ])
    return model


def train_model(X_train, y_train):
    model = create_model()

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    early_stop = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10)

    lr_schedule = tf.keras.callbacks.LearningRateScheduler(
        lambda epoch: 1e-3 * 10 ** (epoch / 20)
    )
    model.fit(X_train, y_train, epochs=50, validation_data=(X_test, y_test), callbacks=[early_stop, lr_schedule])

    return model


def extract_features(game):
    # Extract features
    features = [
        game.get("Game Time", 0),
        game.get("Kills", 0),
        game.get("Deaths", 0),
        game.get("Assists", 0),
        game.get("CS", 0) * game.get("Game Time", 0),  # CS per Minute
        game.get("Gold", 0) * game.get("Game Time", 0),  # Gold per Minute
        game.get("Damage Dealt to Champions", 0),
        game.get("Damage Taken", 0),
        game.get("Crowd Control Score", 0),
        game.get("Wards Placed", 0),
        game.get("Wards Killed", 0),
        game.get("Vision Score", 0),
        game.get("TeamID", 0),
    ]
    # Convert boolean win value to integer (1 for True, 0 for False)
    label = 1 if game.get("Win", False) else 0

    return features, label


directory_path = "../players_data"

# List of game file paths to process
player_file_paths = [
]

# Iterate through each game file and store the file paths in a list
for root, _, files in os.walk(directory_path):
    for filename in files:
        if filename.endswith(".json"):
            file_path = os.path.join(root, filename)
            player_file_paths.append(file_path)

all_features, all_labels = np.array([np.empty(13)]), np.array([0])

for filename in player_file_paths:
    with open(filename, "r") as json_file:
        player_data = json.load(json_file)

        # Extracting features and labels
        for game in player_data["games_data"]:
            print(f"Processing game {game['gameId']}")
            feature, label = extract_features(game)
            #print(f"f: {feature}")
            #print(f"shape of feature: {shape(feature)} shape of all_features: {shape(all_features)}")
            all_features = np.append(all_features, [feature], axis=0)
            all_labels = np.append(all_labels, [label], axis=0)
            #print(all_features)

normalized_data = (all_features - np.min(all_features, axis=0)) / (
            np.max(all_features, axis=0) - np.min(all_features, axis=0))

X_train, X_test, y_train, y_test = train_test_split(normalized_data, all_labels, test_size=0.2, random_state=42)

# print first 10 features and labels

model = train_model(X_train, y_train)

# Save model
model.save(f"tensorflow_models/{time.time()}")

# Evaluate model on test set
loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {accuracy * 100:.2f}%")
