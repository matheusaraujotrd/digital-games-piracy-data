from pymongo import MongoClient
import requests as rq

steam_url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"

client = MongoClient('mongodb://localhost:27017')
db = client['jogos_digitais']
collection = db['steam_appid']

response = rq.get(steam_url)

data = response.json()

if 'applist' in data and 'apps' in data['applist']:
    jogos_steam = data['applist']['apps']
    collection.insert_many(jogos_steam)
    print('Dados inseridos com sucesso no MongoDB.')
else:
    print('Erro ao obter dados da API da Steam.')