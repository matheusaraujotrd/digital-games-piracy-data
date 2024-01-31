import requests as rq
import re
import os
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

CONNECTION_STRING_CLOUD = os.getenv('CONNECTION_STRING_CLOUD')
DB = os.getenv('DB')
CRACKLIST = os.getenv('CRACKLIST')
PC_GAMING_WIKI = os.getenv('PC_GAMING_WIKI')
STEAM = os.getenv('STEAM')

STEAM_AK = os.getenv('STEAM_AK')
# Um sistema muito precário de paginação feito a base de muito desespero e falta de tempo

def standardize_name(name):
    standardized_name = re.sub(r'[^a-zA-Z0-9\s]+', '', name).lower().strip()
    return re.sub(r'\s+', ' ', standardized_name)

def get_names():
    game_names = []
    game_appids = []
    request = rq.get(f"https://api.steampowered.com/ISteamApps/GetAppList/v2/?access_token={STEAM_AK}")
    data = request.json()
    for item in data["applist"]["apps"]:
        game_names.append(item["name"])
        game_appids.append(item["appid"])
    game_names = [standardize_name(name) for name in game_names]
    return game_names, game_appids

def games_from_cracks(cracks_collection):
    games_collected = cracks_collection.distinct("name")
    return games_collected

def compare(game_names, game_details, cracks_collection, appids_from_steam):
    missing_names = []
    missing_appids = []
    for name, appid in zip(game_names, appids_from_steam):
        if name in game_details and name not in cracks_collection:
            missing_names.append(name)
            missing_appids.append(appid)
    return missing_names, missing_appids

def main():
    client = MongoClient(CONNECTION_STRING_CLOUD)
    db = client[DB]
    cracks_collection = db[CRACKLIST]
    steam_collection = db[STEAM]
    game_details_collection = db[PC_GAMING_WIKI]

    # Obtendo os nomes dos jogos da Steam
    game_names_from_steam, appids_from_steam = get_names()

    # Obtendo os nomes dos jogos da coleção de cracks
    games_names_details = game_details_collection.distinct("Page")
    games_names_cracks = cracks_collection.distinct("name")

    # Comparando e obtendo os appids ausentes
    missing_names, missing_appids = compare(game_names_from_steam, games_names_details, games_names_cracks, appids_from_steam)
    print(len(missing_names))
    print(missing_names)
    return missing_appids, missing_names



if __name__ == "__main__":
    main()
