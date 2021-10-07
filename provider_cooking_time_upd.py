import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import pandas as pd
import time
import re
import datetime
from utils.admin_panel import AdminPanel
from settings.config import username, password, database, chromedriver, base_admin_panel_url, old_base_admin_panel_url
from settings.config import scope, doc_url, js_dump
import os

creds = ServiceAccountCredentials.from_json_keyfile_dict(js_dump, scope) #initialise credentials for GSheet API
sheetname = os.path.basename(__file__) #get name of the current script and use it to find a list with same name in Gsheet file
client = gspread.authorize(creds) #Connect to API
spreadsheet = client.open_by_url(doc_url) #Open spreadsheet
database = spreadsheet.worksheet(sheetname) #Open the needed list
df = pd.DataFrame(database.get_all_records()).fillna('') #Read data for script
print('Spreadsheet data from', sheetname, 'list has been read.')
driver = webdriver.Chrome(chromedriver) #Initialise driver from bin folder
admin_panel = AdminPanel(driver = driver)
admin_panel.login(username = username, password = password)
driver.maximize_window()  # makes it full screen

for i in range(len(df)):
        x = base_admin_panel_url + "/delivery/providers/" + str(df.iloc[i, 0])
        driver.get(x)
        time.sleep(2)
        driver.implicitly_wait(100)
        # Cooking time
        ct_box = driver.find_element_by_name("average_cooking_time")
        # delete old
        [ct_box.send_keys(Keys.BACKSPACE) for n in range(0,8)]
        time.sleep(1)
        ct_box.send_keys(str(df.iloc[i, 1]))
        driver.implicitly_wait(50)
        admin_panel.save_provider() #Save changes
        print(x, round((i + 1) / len(df), 2), 'completed from total', datetime.datetime.now())
print("Done all done, closing chrome.")
driver.close()