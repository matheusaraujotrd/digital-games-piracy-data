import requests as rq
from bs4 import BeautifulSoup
import re

def standardNames(text_list):
    standardized_names = []

    for name in text_list:
        standardized_name = re.sub(r'[^a-zA-Z0-9\s]+', '', name).lower().strip()
        standardized_name = re.sub(r'\s+', ' ', standardized_name)
        standardized_names.append(standardized_name)
    return standardized_names


def getRecords(soup):
    records = soup.find_all("th", class_="table-DRM-body-game")
    text_list = [record.text for record in records]
    standardized_names = standardNames(text_list)
    return standardized_names

def getDenuvoList():
    url = "https://www.pcgamingwiki.com/wiki/Denuvo"

    request = rq.get(url)

    request = request.content

    soup = BeautifulSoup(request, "html.parser")

    standardized_names = getRecords(soup)
    return standardized_names

getDenuvoList()