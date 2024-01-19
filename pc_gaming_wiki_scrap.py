import requests as rq
from bs4 import BeautifulSoup
import re

def standardize_name(name):
    standardized_name = re.sub(r'[^a-zA-Z0-9\s]+', '', name).lower().strip()
    return re.sub(r'\s+', ' ', standardized_name)

def extract_text_list(soup, tag, class_name):
    elements = soup.find_all(tag, class_=class_name)
    return [element.text for element in elements]

def get_records(soup, tag, class_name):
    text_list = extract_text_list(soup, tag, class_name)
    return [standardize_name(name) for name in text_list]

def get_denuvo_list(url):
    request = rq.get(url)
    soup = BeautifulSoup(request.content, "html.parser")
    standardized_names = get_records(soup, "th", "table-DRM-body-game")
    return standardized_names

def main():
    denuvo_url = "https://www.pcgamingwiki.com/wiki/Denuvo"
    denuvo_list = get_denuvo_list(denuvo_url)
    
    # Do something with the standardized names (print or save to a file, for example)
    print("Standardized Denuvo Names:", denuvo_list)

if __name__ == "__main__":
    main()
