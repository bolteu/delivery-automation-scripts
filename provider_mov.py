import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
from utils.driver import driver
import time
import re
import datetime
from utils.admin_panel import AdminPanel
from settings.config import username, password, database, chromedriver, base_admin_panel_url, old_base_admin_panel_url
from settings.config import scope, doc_url, js_dump
import json
import os

creds = ServiceAccountCredentials.from_json_keyfile_dict(js_dump, scope) #initialise credentials for GSheet API
sheetname = os.path.basename(__file__) #get name of the current script and use it to find a list with same name in Gsheet file
client = gspread.authorize(creds) #Connect to API
spreadsheet = client.open_by_url(doc_url) #Open spreadsheet
database = spreadsheet.worksheet(sheetname) #Open the needed list
df = pd.DataFrame(database.get_all_records()).fillna('') #Read data for script
print('Spreadsheet data from', sheetname, 'list has been read.')
 #Initialise driver from bin folder
admin_panel = AdminPanel(driver = driver)
admin_panel.login(username = username, password = password)
driver.maximize_window()  # makes it full screen

for i in range(len(df)):
        x = admin_panel.provider_url(df.iloc[i, 0])
        n_mov = str(df.iloc[i, 1])
        n_msof = str(df.iloc[i, 2])
        driver.get(x)
        time.sleep(1.5)
        driver.implicitly_wait(100)
        mov_box = driver.find_element(By.NAME, 'min_order_price')
        [mov_box.send_keys(Keys.BACKSPACE) for n in range(0,15)] # remove old fee max 15 characters
        time.sleep(1)
        mov_box.send_keys(n_mov) #add new fee
        time.sleep(1)
        msof_box = driver.find_element(By.NAME, 'small_order_fee_cap')
        [msof_box.send_keys(Keys.BACKSPACE) for n in range(0,15)]  # remove old MSOF max 15 characters
        time.sleep(1)
        msof_box.send_keys(n_msof)  # add new MSOF fee
        # Save changes
        time.sleep(1)
        admin_panel.save_provider()
        print(x, round((i + 1) / len(df), 2), 'completed from total', datetime.datetime.now())
print("Done all done, closing chrome.")
driver.close()
