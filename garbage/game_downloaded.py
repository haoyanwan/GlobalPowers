import requests
import json
import gzip
import shutil
import time
import os
from io import BytesIO

S3_BUCKET_URL = "https://power-rankings-dataset-gprhack.s3.us-west-2.amazonaws.com"


def download_gzip_and_write_to_json(file_name, output_directory):
    local_file_name = file_name.replace(":", "_")
    # If file already exists locally do not re-download the game
    if os.path.isfile(f"{output_directory}/{local_file_name}.json"):
        return

    file_name = "esports-data/" + file_name #"games_data/"

    response = requests.get(f"{S3_BUCKET_URL}/{file_name}.json.gz")
    if response.status_code == 200:
        try:
            gzip_bytes = BytesIO(response.content)
            with gzip.GzipFile(fileobj=gzip_bytes, mode="rb") as gzipped_file:
                with open(f"{output_directory}/{local_file_name}.json", 'wb') as output_file:
                    shutil.copyfileobj(gzipped_file, output_file)
            print(f"{file_name}.json written")
        except Exception as e:
            print("Error:", e)
    else:
        print(f"Failed to download {file_name}")


def download_esports_files():
    directory = "esports-data"
    if not os.path.exists(directory):
        os.makedirs(directory)

    esports_data_files = ["leagues", "tournaments", "players", "teams", "mapping_data"]
    for file_name in esports_data_files:
        download_gzip_and_write_to_json(file_name, directory)


def create_game_directory_structure(year, tournament, stage, section):
    directory = f"games_data/{year}/{tournament}/{stage}/{section}"
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory


def download_games(year):
    start_time = time.time()
    with open("esports-data/tournaments.json", "r") as json_file:
        tournaments_data = json.load(json_file)
    with open("esports-data/mapping_data.json", "r") as json_file:
        mappings_data = json.load(json_file)

    mappings = {
        esports_game["esportsGameId"]: esports_game for esports_game in mappings_data
    }



    for tournament in tournaments_data:
        tournament_slug = tournament.get("slug", "no-tournament")
        print(f"Processing {tournament_slug}")
        start_date = tournament.get("startDate", "")
        if start_date.startswith(str(year)):
            for stage in tournament["stages"]:
                stage_slug = stage.get("slug", "no-stage")
                for section in stage.get("sections", []):  # Check if "sections" exists
                    section_slug = section.get("slug", "no-section")
                    directory = create_game_directory_structure(tournament_slug, stage_slug, section_slug)
                    for match in section.get("matches", []):  # Check if "matches" exists
                        for game in match.get("games_data", []):  # Check if "games_data" exists
                            if game["state"] == "completed":
                                try:
                                    platform_game_id = mappings[game["id"]]["platformGameId"]
                                    download_gzip_and_write_to_json(platform_game_id, directory)
                                except KeyError:
                                    print(f"{platform_game_id} {game['id']} not found in the mapping table")

            print(
                f"----- Processed {tournament_slug} games_data, current run time: "
                f"{round((time.time() - start_time) / 60, 2)} minutes"
            )


if __name__ == "__main__":
    download_esports_files()

    download_games(2019)


