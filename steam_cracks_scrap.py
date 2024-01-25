import re
import os
import requests as rq
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient
from selenium import webdriver
import missing_appids
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
load_dotenv()

CONNECTION_STRING_CLOUD = os.getenv('CONNECTION_STRING_CLOUD')
DB = os.getenv('DB')
CRACKLIST = os.getenv('CRACKLIST')
PC_GAMING_WIKI = os.getenv('PC_GAMING_WIKI')

def setup_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--lang=en-US")  # Set Brazilian Portuguese language
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)
    return driver


def connect_to_mongodb():
    client = MongoClient(CONNECTION_STRING_CLOUD)
    db = client[DB]
    cracks_collection = db[CRACKLIST]
    game_details_collection = db[PC_GAMING_WIKI]
    return game_details_collection, cracks_collection


def url_linkname(standardized_name):
    return re.sub(r'\s+', '-', standardized_name)


def standardize_name(name):
    standardized_name = re.sub(r'[^a-zA-Z0-9\s]+', '', name).lower().strip()
    return re.sub(r'\s+', ' ', standardized_name)


def convertDate(date):
    
    if date != "---":
        date_format = "%Y-%m-%d"
        datetime_object = datetime.strptime(date, date_format)
        return datetime_object
    else:
        return date


def get_difference(release_date, crack_date):

    if crack_date == "---":
        crack_date = datetime(2024, 1, 21, 00, 00)
    time_difference = crack_date - release_date
    days_difference = time_difference.days
    return days_difference


def fetch_game_names(game_details_collection, file=None, restore_appids=None):
    game_names = []
    if file:
        f = open(file, "r")
        f = f.read()
        f = f.split("\n")
        for game in f:
            game_standardized = standardize_name(game)
            game_names.append(game_standardized)
        return game_names
    elif restore_appids == True:
        missing_collection_appids, missing_collection_names = missing_appids.main()
        return missing_collection_appids, missing_collection_names
    else:
        return list(game_details_collection.distinct('Page'))


def get_page_source(driver, link):
    try:
        driver.get(link)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "title-navigator")))
    except TimeoutException as e:
        print("Página não encontrada para o jogo requisitado.")
    try:
        html = driver.page_source
    except TimeoutException:
        print("Tempo de espera excedido! Próximo jogo...")
    soup = BeautifulSoup(html, "html.parser")
    return soup


def get_data(soup):
    document = {
        'name': None,
        'crack_status': None,
        'crack_team': None,
        'drm': None,
        'release_date': None,
        'crack_date': None,
        'dates_dif': None,
    }

    title = soup.find('div', class_='title-navigator title-navigator-min')
    if title:
        name = title.h1
        name = ''.join(name.find_all(text=True, recursive=False)).strip()
        wrapper_div = soup.find('div', class_='info-game-wrapper')
        if wrapper_div:
            print("Jogo encontrado!")
            status_div = wrapper_div.find('div', class_='game-status protect-bottom')
            crack_status = status_div.find('p', class_='game-info-def-text').text.strip()
            value_list = wrapper_div.find_all('p', class_='game-info-value')
            document["crack_status"] = crack_status
            document['release_date'] = value_list[0].text.strip()
            document['crack_date'] = value_list[3].text.strip()
            document['crack_team'] = value_list[2].text.strip()
            document['drm'] = value_list[1].text.strip()

            # Data transform
            document["release_date"] = convertDate(document["release_date"])
            document["crack_date"] = convertDate(document["crack_date"])
            document["name"] = standardize_name(name)
            days_difference = get_difference(document["release_date"], document["crack_date"])
            document["dates_dif"] = days_difference
            # difference as of 21/01/2024
            return document
        else:
            print("Impossível obter dados do jogo. O site parece não conter o jogo no banco de dados")
            return None
    else:
        print("Impossível obter dados do jogo. O site parece não conter o jogo no banco de dados")
        return None


def insert_on_database(document, cracks_collection):
    if document:
        existing_document = cracks_collection.find_one({'name': document['name']})
        if not existing_document:
            cracks_collection.insert_one(document)
            print(f"Jogo {document['name']} adicionado.")
        else:
            print("Jogo já existe no banco de dados, pulando...")



def main():
    driver = setup_chrome_driver()
    game_details_collection, cracks_collection = connect_to_mongodb()
    appids, game_names = fetch_game_names(game_details_collection, file=None, restore_appids=True)

    for name in game_names:
        link_name = url_linkname(name)
        url = f'https://gamestatus.info/{link_name}/en'
        soup = get_page_source(driver, url)
        if soup:
            document = get_data(soup)
            insert_on_database(document, cracks_collection)
        else:
            print(f"Impossível obter dados para o jogo {name} agora.")

if __name__ == "__main__":
    main()
    