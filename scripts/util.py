import dotenv
import re
import os
import logging
import requests as rq
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService

load_dotenv()

def load_variables():
    CONNECTION_STRING_CLOUD = os.getenv('CONNECTION_STRING_CLOUD')
    DB = os.getenv('DB')
    STEAM = os.getenv('STEAM')
    PC_GAMING_WIKI = os.getenv('PC_GAMING_WIKI')
    CRACKLIST = os.getenv('CRACKLIST')
    BUCKET = os.getenv('BUCKET')
    BUCKET_STAGING = os.getenv('BUCKET_STAGING')
    TEMPLATE_LOCATION = os.getenv('TEMPLATE_LOCATION')
    STEAM_KEY = os.getenv('STEAM_KEY')
    STEAM_AK = os.getenv('STEAM_AK')

def standardize_name(name):
    standardized_name = re.sub(r'[^a-zA-Z0-9\s]+', '', name).lower().strip()
    return re.sub(r'\s+', ' ', standardized_name)