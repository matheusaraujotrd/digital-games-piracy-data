import requests as rq
from bs4 import BeautifulSoup
import re
# This is just a simple script to get all games with denuvo from PC Gaming Wiki.
# I've used this script only once.

# To update denuvo games only, prefer this script than pc_gaming_wiki_api_update, because Steam database is HUUUGE

def get_denuvo_list(url):
    request = rq.get(url)
    soup = BeautifulSoup(request.content, "html.parser")
    elements = soup.find_all("th", class_="table-DRM-body-game")
    return [element.text for element in elements]


def compile_denuvo():
    denuvo_url = "https://www.pcgamingwiki.com/wiki/Denuvo"
    denuvo_list = get_denuvo_list(denuvo_url)
    return denuvo_list


def write_to_file(denuvo_list):
    f = open("denuvo_list.txt","w+", encoding="utf-8")
    for game in denuvo_list:
        f.write(f"{game}\n")


def main():
    denuvo_list = compile_denuvo()
    write_to_file(denuvo_list)


if __name__ == "__main__":
    main()
