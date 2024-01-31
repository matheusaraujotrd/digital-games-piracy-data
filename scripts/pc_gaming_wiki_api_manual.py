from pymongo import MongoClient
from dotenv import load_dotenv
import requests as rq
import os
import re
load_dotenv()

CONNECTION_STRING_CLOUD = os.getenv('CONNECTION_STRING_CLOUD')
DB = os.getenv('DB')
PC_GAMING_WIKI = os.getenv('PC_GAMING_WIKI')

def standardize_name(name):
    standardized_name = re.sub(r'[^a-zA-Z0-9\s]+', '', name).lower().strip()
    return re.sub(r'\s+', ' ', standardized_name)

f = open("steam_appids_most_played.txt", "r")
f = f.read()
f = f.split("\n")

client = MongoClient(CONNECTION_STRING_CLOUD)
db = client[DB]
game_details_collection = db[PC_GAMING_WIKI]

for game in f:
    query_url = f'https://www.pcgamingwiki.com/w/api.php?action=cargoquery&format=json&tables=Availability,Infobox_game&fields=Infobox_game._pageName=Page,Availability.Battlenet_DRM,Availability.EA_Desktop_DRM,Availability.EA_Play,Availability.EA_Play_Pro,Availability.EA_Play_Steam,Availability.Epic_Games_Store_DRM,Availability.Steam_DRM,Availability.Ubisoft_Plus,Infobox_game.Available_on,Infobox_game.Developers,Infobox_game.Genres,Infobox_game.Monetization,Infobox_game.Modes,Infobox_game.Publishers,Infobox_game.Released,Infobox_game.Released_Windows,Availability.Removed_DRM&join_on=Infobox_game._pageID=Availability._pageID&where=Infobox_game.Steam_AppID%20HOLDS%20"{game}"'
    
    try:
        request = rq.get(query_url)
        data = request.json()
    except rq.RequestException as e:
        print(f"Erro ao obter dados do appid {game} para a API PC Gaming Wiki: {e}")
        data = None

    try:
        if 'cargoquery' in data and 'title' in data['cargoquery'][0]:
            standardized_name = standardize_name(data['cargoquery'][0]['title']['Page'])
            data['cargoquery'][0]['title']['Page'] = standardized_name
            
            if game_details_collection.count_documents({"Page": standardized_name}) > 0:
                print(f'Game "{data["cargoquery"][0]["title"]["Page"]}" já existe na coleção. Pulando...')
                continue
            else:
                game_details_collection.insert_one(data['cargoquery'][0]['title'])
                print('Dados enviados com sucesso à coleção game_details.')
        else:
            print('Erro ao obter dados via PC Gaming Wiki API.')
    except IndexError as e:
        print("O jogo não tem informações disponíveis na API. Pulando...")
client.close()