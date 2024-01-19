from pymongo import MongoClient
import requests as rq

game = input("Insira o appID da Steam:\n")

client = MongoClient('mongodb://localhost:27017')
db = client['jogos_digitais']
game_details_collection = db['game_details']

query_url = f'https://www.pcgamingwiki.com/w/api.php?action=cargoquery&format=json&tables=Availability,Infobox_game&fields=Infobox_game._pageName=Page,Availability.Battlenet_DRM,Availability.EA_Desktop_DRM,Availability.EA_Play,Availability.EA_Play_Pro,Availability.EA_Play_Steam,Availability.Epic_Games_Store_DRM,Availability.Steam_DRM,Availability.Ubisoft_Plus,Infobox_game.Available_on,Infobox_game.Developers,Infobox_game.Genres,Infobox_game.Monetization,Infobox_game.Modes,Infobox_game.Publishers,Infobox_game.Released,Infobox_game.Released_Windows,Availability.Removed_DRM&join_on=Infobox_game._pageID=Availability._pageID&where=Infobox_game.Steam_AppID%20HOLDS%20"{game}"'
    
request = rq.get(query_url)
data = request.json()

if 'cargoquery' in data and 'title' in data['cargoquery'][0]:
    game_details_collection.insert_one(data['cargoquery'][0]['title'])
    print('Dados enviados com sucesso à coleção game_details.')
else:
    print('Erro ao obter dados via PC Gaming Wiki API.')