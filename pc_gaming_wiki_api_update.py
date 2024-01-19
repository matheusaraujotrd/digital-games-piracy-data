from pymongo import MongoClient
import requests as rq
import re

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

# Verifies if data queried through API is valid, checks the database for duplicates, standardize the name and add it to collection
# Might need to refactor it later
def process_and_store_data(data, game_details_collection, app_id):
    try:
        if 'cargoquery' in data and 'title' in data['cargoquery'][0]:
            for item in data['cargoquery']:
                if 'title' not in item:
                    raise ValueError('Erro ao obter dados da API PC Gaming Wiki.')

                standardized_name = re.sub(r'[^a-zA-Z0-9\s]+', '', item["title"]["Page"]).lower().strip()
                standardized_name = re.sub(r'\s+', ' ', standardized_name)

                if game_details_collection.count_documents({"Page": standardized_name}) > 0:
                    print(f'Game "{item["title"]["Page"]}" já existe na coleção. Pulando...')
                    continue

                item["title"]["Page"] = standardized_name
                game_details_collection.insert_one(item['title'])
                print(f'Dados do appID {app_id} adicionados com sucesso à coleção game_details.')
    except IndexError as e:
        print(f"appid {app_id} não tem informações disponíveis na API. Pulando...")


# Main function
def game_details():
    client = MongoClient('mongodb://localhost:27017')
    db = client['jogos_digitais']
    steam_collection = db['steam_appid']
    game_details_collection = db['game_details']

    try:
        app_ids = query_steam_appids(steam_collection)

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
