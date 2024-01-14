from pymongo import MongoClient
import requests as rq
import pc_gaming_wiki_scrap

denuvoList = pc_gaming_wiki_scrap.getDenuvoList()
appID = []

client = MongoClient('mongodb://localhost:27017')
db = client['jogos_digitais']
steam_collection = db['steam_appid']
game_details_collection = db['game_details']

# Find documents in steam_appid collection where "name" matches any value in denuvoList
result = steam_collection.find({"name": {"$in": denuvoList}})

# Iterate through the matching documents and extract appid values
for document in result:
    appid_value = document.get("appid")
    if appid_value is not None:
        appID.append(appid_value)

# Iterate through appID and query PC Gaming Wiki API for each app ID
for appid in appID:
    query_url = f'https://www.pcgamingwiki.com/w/api.php?action=cargoquery&format=json&tables=Availability,Infobox_game&fields=Infobox_game._pageName=Page,Availability.Battlenet_DRM,Availability.EA_Desktop_DRM,Availability.EA_Play,Availability.EA_Play_Pro,Availability.EA_Play_Steam,Availability.Epic_Games_Store_DRM,Availability.Steam_DRM,Availability.Ubisoft_Plus,Infobox_game.Available_on,Infobox_game.Developers,Infobox_game.Genres,Infobox_game.Monetization,Infobox_game.Modes,Infobox_game.Publishers,Infobox_game.Released,Infobox_game.Released_Windows,Availability.Removed_DRM&join_on=Infobox_game._pageID=Availability._pageID&where=Infobox_game.Steam_AppID%20HOLDS%20"{appid}"'
    
    request = rq.get(query_url)
    data = request.json()

    if 'cargoquery' in data and 'title' in data['cargoquery'][0]:
        existing_document = game_details_collection.find_one({"Page": data['cargoquery'][0]['title']['Page']})
    
        if existing_document:
            print(f'Jogo "{data["cargoquery"][0]["title"]["Page"]}" já existe na coleção. Pulando documento...')
            continue

        game_details_collection.insert_one(data['cargoquery'][0]['title'])
        print(f'Dados enviados com sucesso à coleção game_details para o appID {appid}.')
    else:
        print(f'Erro ao obter dados via PC Gaming Wiki API para o appID {appid}.')
