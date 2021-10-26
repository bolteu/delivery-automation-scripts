import re
from time import sleep
from selenium.common.exceptions import NoSuchElementException
import math
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from settings.config import base_admin_panel_url, old_base_admin_panel_url
from settings.config import scope, doc_url, js_dump
from oauth2client.service_account import ServiceAccountCredentials
import gspread

def api_authorize(js_dump, scope):
    client = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(js_dump, scope))  # Connect to API
    spreadsheet = client.open_by_url(doc_url)  # Open spreadsheet
    return spreadsheet