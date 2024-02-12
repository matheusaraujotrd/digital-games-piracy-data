from data_class import SteamData, GamingWikiData, StatusData
from util import load_variables, standardize_name

import logging
import requests as rq
from bs4 import BeautifulSoup
from pymongo import MongoClient
from selenium import webdriver
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService

# Global logging service
logger = logging.getLogger("DCP")

# Connecting to MongoDB Atlas Cloud
def connecting_to_client(c_string):
    client = MongoClient(c_string)
    logger.info('Conectado ao cliente MongoDB')
    return client


# Connecting to MongoDB database
def connecting_to_database(client, database):
    db = client[database]
    logger.info('Conectado ao banco de dados MongoDB')
    return db


# Connecting to required collection
def connecting_to_collection(database, coll):
    collection = database[coll]
    logger.info('Conectado à coleção solicitada.')
    return collection


# Closing the connection
def kill_connection(client) -> None:
    try:
        client.close()
    except PyMongoError as e:
        logger.error(f"Erro ao encerrar conexão MongoDB: {e}")
    logger.info("Conexão com o MongoDB encerrada.")


# Main scraping function
def run(variables: dict, logger, Steam=False, Gaming_Wiki=False, Game_Status=False) -> None:
    mongo_client = connecting_to_client(variables['CONNECTION_STRING_CLOUD'])
    mongo_db = connecting_to_database(mongo_client, variables['DB'])

    if Steam:
        scrape_steam(mongo_db, variables)
    
    if Gaming_Wiki:
        scrape_pc_gaming_wiki(mongo_db, variables)
    
    if Game_Status:
        pass

    kill_connection(mongo_client)
    logging.shutdown()


def scrape_steam(database, variables):
        
    # Booting MongoDB connections
    steam_collection = connecting_to_collection(database, variables['STEAM'])

    logger.info(steam_collection.count_documents({}))
    request = rq.get(f"https://api.steampowered.com/ISteamApps/GetAppList/v2/?access_token={variables['STEAM_AK']}")

    # Checking if request was successful
    if request.status_code == 200:
        # Saving data to json format
        data = request.json()
        # Checking if collection is empty
        if steam_collection.count_documents({}) == 0:
            # Iterating with games, creating the SteamData structure
            for item in data['applist']['apps']:
                newGame = SteamData(
                    item['name'], 
                    standardize_name(item['name']), 
                    item['appid'])
                # Validating if the name is not empty and then adding the game to collection
                if newGame.validate_name():
                    logger.info(f'{newGame.get_name()} (appid {newGame.get_appid()}) coletado!')
                    steam_collection.insert_one(newGame.to_document())
        else:
            # If collection is not empty, first checks if the game is already into collection before adding it
            for item in data['applist']['apps']:
                newGame = SteamData(item['name'], standardize_name(item['name']), item['appid'])
                if steam_collection.find_one({'appid': newGame.get_appid}) is None and newGame.validate_name():
                    logger.info(f'{newGame.get_name()} (appid {newGame.get_appid()}) coletado!')
                    steam_collection.insert_one(newGame.to_document())

    else:
        logger.error('Falha em contatar a API steam...')
        return


def scrape_pc_gaming_wiki(database, variables):

    # Booting MongoDB connections
    steam_collection = connecting_to_collection(database, variables['STEAM'])
    gaming_wiki_collection = connecting_to_collection(database, variables["PC_GAMING_WIKI"])

    retries = 0
    n1 = 0
    n2 = 0

    appids = steam_collection.distinct('appid')
    appids_used = gaming_wiki_collection.distinct('appid')
    # Iterating over available games on steam collection
    for appid in appids:
        n1 += 1
        '''
        Below line checks if the game is not 
        already on pc gaming wiki collection...
        Currently, this query is creating duplicate results
        because some games are registered with more than one appid.
        Unfortunately, this is not surmountable at query time, so
        this is solved at a later transformation step.
        '''
        if appid not in appids_used:
            # PC Gaming Wiki query
            query = (
                'https://www.pcgamingwiki.com/w/api.php?action=cargoquery'
                '&format=json'
                '&tables=Availability,Infobox_game'
                '&fields=Infobox_game._pageName=Page,Availability.Steam_DRM,'
                'Infobox_game.Available_on,Infobox_game.Developers,'
                'Infobox_game.Genres,Infobox_game.Monetization,Infobox_game.Modes,'
                'Infobox_game.Publishers,Infobox_game.Released,Infobox_game.Released_Windows,Availability.Removed_DRM'
                '&join_on=Infobox_game._pageID=Availability._pageID'
                f'&where=Infobox_game.Steam_AppID%20HOLDS%20"{appid}"'
            )
            try:
                request = rq.get(query)
                data = request.json()
            except rq.RequestException as e:
                logger.error(f'Não foi possível acessar o endpoint da API: {e}')
                retries += 1
                logger.info(f"Tentativa número {retries}. O sistema desligará após 3 tentativas seguidas.")
                if retries == 3:
                    return

            try:
                retries = 0
                # Checking if the game has data on PC Gaming Wiki, then adding to collection
                if 'title' in data['cargoquery'][0]:
                        
                    # GamingWikiData structure creation
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
                        
                    n2+= 1
                    logger.info(f'{newGameDetails.get_name()} adicionado.\n{n1} jogo(s) analisados, {n2} jogo(s) adicionados.')
                    gaming_wiki_collection.insert_one(newGameDetails.to_document())

            except IndexError:
                game = steam_collection.find_one({'appid': appid})
                logger.warning(f'Nenhum dado encontrado para o jogo {appid} - {game["nome"]}...\n{n1} jogo(s) analisados.')
        else:
            game = gaming_wiki_collection.find_one({'appid': appid})
            logger.info(f'Jogo {appid} - {game["nome"]} já está no banco de dados. Próximo jogo...\n{n1} jogo(s) analisados.')