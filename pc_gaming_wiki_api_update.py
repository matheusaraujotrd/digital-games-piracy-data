from pymongo import MongoClient
from dotenv import load_dotenv
import requests as rq
import os
import re
load_dotenv()

CONNECTION_STRING_CLOUD = os.getenv('CONNECTION_STRING_CLOUD')
DB = os.getenv('DB')
PC_GAMING_WIKI = os.getenv('PC_GAMING_WIKI')
STEAM = os.getenv('STEAM')


# This is my mains script to do games ingestion.
# I get all steam appids from database and then do an API search for each of them.

# Be aware that steam has almost 186k appids, so this take a while and is not really recommended if you're just looking to update an already existing database.

# Return appids from Steam MongoDB database
def query_steam_appids(steam_collection):
    print("Buscando appids na coleção Steam Appids...")
    result = steam_collection.find({"name": {"$ne": None, "$exists": True, "$ne": ''}})
    app_ids = [document.get("appid") for document in result if document.get("appid")]

    return app_ids

# Queries the PC Gaming Wiki API with requested appid
def query_pc_gaming_wiki(app_id):
    print(f"Buscando appid {app_id} na API PC Gaming Wiki")
    query_url = f'https://www.pcgamingwiki.com/w/api.php?action=cargoquery&format=json&tables=Availability,Infobox_game&fields=Infobox_game._pageName=Page,Availability.Battlenet_DRM,Availability.EA_Desktop_DRM,Availability.EA_Play,Availability.EA_Play_Pro,Availability.EA_Play_Steam,Availability.Epic_Games_Store_DRM,Availability.Steam_DRM,Availability.Ubisoft_Plus,Infobox_game.Available_on,Infobox_game.Developers,Infobox_game.Genres,Infobox_game.Monetization,Infobox_game.Modes,Infobox_game.Publishers,Infobox_game.Released,Infobox_game.Released_Windows,Availability.Removed_DRM&join_on=Infobox_game._pageID=Availability._pageID&where=Infobox_game.Steam_AppID%20HOLDS%20"{app_id}"'

    try:
        request = rq.get(query_url)
        data = request.json()
        return data
    except rq.RequestException as e:
        print(f"Erro ao obter dados do appid {app_id} para a API PC Gaming Wiki: {e}")
        return None

# Standardizes names
def standardize_name(name):
    standardized_name = re.sub(r'[^a-zA-Z0-9\s]+', '', name).lower().strip()
    return re.sub(r'\s+', ' ', standardized_name)

    
# Verifies if data queried through API is valid, checks the database for duplicates, standardize the name and add it to collection
# Might need to refactor it later
def process_and_store_data(data, game_details_collection, app_id):
    try:
        if 'cargoquery' in data and 'title' in data['cargoquery'][0]:
            for item in data['cargoquery']:
                if 'title' not in item:
                    raise ValueError('Erro ao obter dados da API PC Gaming Wiki.')

                standardized_name = standardize_name(item["title"]["Page"])

                if game_details_collection.count_documents({"Page": standardized_name}) > 0:
                    print(f'Game "{item["title"]["Page"]}" já existe na coleção. Pulando...')
                    continue

                item["title"]["Page"] = standardized_name
                game_details_collection.insert_one(item['title'])
                print(f'Dados do appID "{app_id} - {standardized_name}" adicionados com sucesso à coleção game_details.')
        else:
            print(f"appid {app_id} não tem informações disponíveis na API. Pulando...")
    except IndexError as e:
        print(f"appid {app_id} não tem informações disponíveis na API. Pulando...")


def check_duplicates_appids(app_ids, steam_collection, game_details_collection):
    unique_app_ids = []
    
    print("Verificando appids duplicados para reduzir o número de requisições de API:\n")
    for app_id in app_ids:
        app_id_name = steam_collection.find_one({"appid": app_id})
        
        if not game_details_collection.count_documents({"Page": app_id_name}):
            print(f"Appid {app_id} único!")
            unique_app_ids.append(app_id)
        else:
            print(f"{app_id} - {app_id_name} já no banco de dados.")
    
    return unique_app_ids


# Main function
def game_details():
    client = MongoClient(CONNECTION_STRING_CLOUD)
    db = client[DB]
    steam_collection = db[STEAM]
    game_details_collection = db[PC_GAMING_WIKI]

    try:
        app_ids = query_steam_appids(steam_collection)
        app_ids = check_duplicates_appids(app_ids, steam_collection, game_details_collection)

        for app_id in app_ids:
            data = query_pc_gaming_wiki(app_id)

            if data:
                process_and_store_data(data, game_details_collection, app_id)

    except Exception as e:
        print(f'Erro ao processar detalhes do jogo: {e}')

    finally:
        client.close()

if __name__ == "__main__":
    game_details()
