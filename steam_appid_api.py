from pymongo import MongoClient
import requests as rq
import re

client = MongoClient('mongodb://localhost:27017')
db = client['jogos_digitais']
collection = db['steam_appid']

def standardNames():
    original_names = collection.distinct("name")
    standardized_names = []
    for name in original_names:
        standardized_name = re.sub(r'[^a-zA-Z0-9\s]+', '', name).lower().strip()
        standardized_names.append(standardized_name)
    for original_name, standardized_name in zip(original_names, standardized_names):
        collection.update_one({"name": original_name}, {"$set": {"name": standardized_name}})
    print("Nomes atualizados com sucesso no MongoDB.")

def fullIngestion():
    steam_url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"

    response = rq.get(steam_url)

    data = response.json()

    if 'applist' in data and 'apps' in data['applist']:
        jogos_steam = data['applist']['apps']
        for game in jogos_steam:
            original_name = game.get("name", "")
            standardized_name = re.sub(r'[^a-zA-Z0-9\s]+', '', original_name).lower().strip()
            standardized_name = re.sub(r'\s+', ' ', standardized_name)
            game["name"] = standardized_name
        collection.drop()
        collection.insert_many(jogos_steam)
        print('Dados inseridos com sucesso no MongoDB.')
    else:
        print('Erro ao obter dados da API da Steam.')

fullIngestion()
client.close()