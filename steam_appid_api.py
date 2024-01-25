from pymongo import MongoClient
from dotenv import load_dotenv
import requests as rq
import os
import re
load_dotenv()


# Simple script to gather all appids from Steam.

def connect_to_mongodb():
    client = MongoClient(CONNECTION_STRING_CLOUD)
    db = client[DB]
    collection = db[STEAM]
    return client, collection

def standardize_names(original_names, collection):
    standardized_names = [re.sub(r'[^a-zA-Z0-9\s]+', '', name).lower().strip() for name in original_names]

    for original_name, standardized_name in zip(original_names, standardized_names):
        collection.update_one({"name": original_name}, {"$set": {"name": standardized_name}})
    
    print("Nomes atualizados com sucesso no MongoDB.")

def fetch_steam_data():
    steam_url = f"https://api.steampowered.com/ISteamApps/GetAppList/v2/?access_token={STEAM_AK}"
    response = rq.get(steam_url)

    if response.status_code == 200:
        data = response.json()
        if 'applist' in data and 'apps' in data['applist']:
            return data['applist']['apps']
        else:
            print('Erro ao obter dados da API da Steam.')
    else:
        print(f'Erro na requisição da API da Steam. Status code: {response.status_code}')

def full_ingestion(collection):
    steam_data = fetch_steam_data()

    if steam_data:
        for game in steam_data:
            original_name = game.get("name", "")
            standardized_name = re.sub(r'[^a-zA-Z0-9\s]+', '', original_name).lower().strip()
            standardized_name = re.sub(r'\s+', ' ', standardized_name)
            game["name"] = standardized_name

        collection.drop()
        collection.insert_many(steam_data)
        print('Dados inseridos com sucesso no MongoDB.')

def main():
    client, collection = connect_to_mongodb()

    # Standardize names in the MongoDB collection
    original_names = collection.distinct("name")
    standardize_names(original_names, collection)

    # Perform a full ingestion from the Steam API
    full_ingestion(collection)

    client.close()

if __name__ == "__main__":
    main()
