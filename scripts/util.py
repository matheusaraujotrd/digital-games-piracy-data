import dotenv
import re
import os
from dotenv import load_dotenv
from datetime import datetime

def load_variables():
    load_dotenv()
    return {
        'CONNECTION_STRING_CLOUD': os.getenv('CONNECTION_STRING_CLOUD'),
        'DB': os.getenv('DB'),
        'STEAM': os.getenv('STEAM'),
        'PC_GAMING_WIKI': os.getenv('PC_GAMING_WIKI'),
        'CRACKLIST': os.getenv('CRACKLIST'),
        'BUCKET': os.getenv('BUCKET'),
        'BUCKET_STAGING': os.getenv('BUCKET_STAGING'),
        'TEMPLATE_LOCATION': os.getenv('TEMPLATE_LOCATION'),
        'STEAM_KEY': os.getenv('STEAM_KEY'),
        'STEAM_AK': os.getenv('STEAM_AK'),
        'TWITCH_ID': os.getenv('TWITCH_ID'),
        'TWITCH_SECRET': os.getenv('TWITCH_SECRET')
    }

def standardize_name(name):
    standardized_name = re.sub(r'[^a-zA-Z0-9\s]+', '', name).lower().strip()
    return re.sub(r'\s+', ' ', standardized_name)