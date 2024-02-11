import logging
from util import load_variables, standardize_name
import requests as rq
from data_class import SteamData, GamingWikiData, StatusData
from bs4 import BeautifulSoup
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService


def seek_and_destroy(url, variables):
    client = MongoClient(variables['CONNECTION_STRING_CLOUD'])
    db = client[variables['DB']]
    steam_collection = db[variables['STEAM']]
    pc_gaming_wiki_collection = db[variables['PC_GAMING_WIKI']]
    gamestatus_collection = db[variables['CRACKLIST']]

    if url == "steam":
        logging.info(steam_collection.count_documents({}))
        request = rq.get(f"https://api.steampowered.com/ISteamApps/GetAppList/v2/?access_token={variables['STEAM_AK']}")
        if request.status_code == 200:
            data = request.json()
            if steam_collection.count_documents({}) == 0:
                for item in data["applist"]["apps"]:
                    newGame = SteamData(item["name"], standardize_name(item["name"]), item["appid"])
                    if newGame.validate_name():
                        logging.info(f"{newGame.get_name()} (appid {newGame.get_appid()}) coletado!")
                        steam_collection.insert_one(newGame.to_document())
            else:
                for item in data["applist"]["apps"]:
                    newGame = SteamData(item["name"], standardize_name(item["name"]), item["appid"])
                    if steam_collection.find_one({'appid': newGame.get_appid}) == None and newGame.validate_name():
                        logging.info(f"{newGame.get_name()} (appid {newGame.get_appid()}) coletado!")
                        steam_collection.insert_one(newGame.to_document())

        else:
            logging.info("Falha em contatar a API steam...")
            client.Close()

    elif url == "pc_gaming_wiki":
        n = 0
        appids = steam_collection.distinct('appid')
        appids_used = pc_gaming_wiki_collection.distinct('appid')
        for appid in appids:
            if appid not in appids_used:
                query = f'https://www.pcgamingwiki.com/w/api.php?action=cargoquery&format=json&tables=Availability,Infobox_game&fields=Infobox_game._pageName=Page,Availability.Steam_DRM,Infobox_game.Available_on,Infobox_game.Developers,Infobox_game.Genres,Infobox_game.Monetization,Infobox_game.Modes,Infobox_game.Publishers,Infobox_game.Released,Infobox_game.Released_Windows,Availability.Removed_DRM&join_on=Infobox_game._pageID=Availability._pageID&where=Infobox_game.Steam_AppID%20HOLDS%20"{appid}"'
                try:
                    request = rq.get(query)
                    data = request.json()
                except rq.RequestException as e:
                    logging.warning(f"Não foi possível acessar o endpoint da API: {e}")
                    continue
                try:
                    if 'title' in data['cargoquery'][0]:
                        # Create a new GamingWikiData object with attributes based on values from the 'title' key
                        newGameDetails = GamingWikiData(
                            data['cargoquery'][0]['title'].get('Page'),
                            standardize_name(data['cargoquery'][0]['title'].get('Page')),
                            appid,
                            data['cargoquery'][0]['title'].get('Steam DRM'),
                            data['cargoquery'][0]['title'].get('Available on'),
                            data['cargoquery'][0]['title'].get('Developers'),
                            data['cargoquery'][0]['title'].get('Genres'),
                            data['cargoquery'][0]['title'].get('Monetization'),
                            data['cargoquery'][0]['title'].get('Modes'),
                            data['cargoquery'][0]['title'].get('Publishers'),
                            data['cargoquery'][0]['title'].get('Released'),
                            data['cargoquery'][0]['title'].get('Released Windows'),
                            data['cargoquery'][0]['title'].get('Removed DRM')
                        )
                        # Print the document representation of the new object
                        n+= 1
                        logging.info(f"{newGameDetails.get_name()} adicionado.\n{n} jogo(s) adicionados.")
                        pc_gaming_wiki_collection.insert_one(newGameDetails.to_document())

                except IndexError:
                    logging.info("Erro de índice, pulando...")
            else:
                logging.info(f"Jogo {appid} já está no banco de dados. Pulando...")
                


    elif url == "gamestatus":
        pass
    
    client.Close()
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    variables = load_variables()
    seek_and_destroy("pc_gaming_wiki", variables)
