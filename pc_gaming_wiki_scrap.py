import requests as rq
from bs4 import BeautifulSoup

def getRecords(soup):
    records = soup.find_all("tr", class_='table-DRM-body-row')
    print(records)

url = "https://www.pcgamingwiki.com/wiki/Denuvo"

request = rq.get(url)

request = request.content

soup = BeautifulSoup(request, "html.parser")

print(soup.prettify())
getRecords(soup)