import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
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
        n_p_earn, n_d_earn = str(df.iloc[i, 1]), str(df.iloc[i, 2])
        driver.get(x)
        time.sleep(1.5)
        driver.implicitly_wait(100)
        p_earn_box = driver.find_element(By.NAME, 'pickup')  #find courier pickup earning box
        d_earn_box = driver.find_element(By.NAME, 'dropoff') #find courier dropoff earning box
        [p_earn_box.send_keys(Keys.BACKSPACE) for n in range(20)] #delete old value of pickup earning
        [d_earn_box.send_keys(Keys.BACKSPACE) for n in range(20)]  # delete old value of dropoff earning
        p_earn_box.send_keys(n_p_earn) #Add new value for pickup earning
        d_earn_box.send_keys(n_d_earn)  # Add new value for pickup earning
        admin_panel.save_provider() #SAVE
        print(x, round((i + 1) / len(df), 2), 'completed from total', datetime.datetime.now())
print("Done all done, closing chrome.")
driver.close()