from bs4 import BeautifulSoup
import requests

host = "crackwatcher"
if host == "crackwatcher":
    url = "https://crackwatcher.com/game/assassins-creed-mirage"
    html = requests.get(url)
    soup = BeautifulSoup(html.content, "html.parser")
    print(soup.prettify())
