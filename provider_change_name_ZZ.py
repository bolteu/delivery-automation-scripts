import gspread
from oauth2client.service_account import ServiceAccountCredentials
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
from selenium.webdriver.common.by import By


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
time.sleep(1)
for i in range(len(df)):
        x = admin_panel.provider_url(df.iloc[i, 0])
        description = str(df.iloc[i, 1])  # assign commission variable
        driver.get(x)
        driver.implicitly_wait(10)
        try:
                name_zz_box = driver.find_element(By.XPATH, "//input[contains(@name, '-ZZ')]") #find zz box
                time.sleep(2)
                current_desc = name_zz_box.get_attribute('value') #get current description
                [name_zz_box.send_keys(Keys.BACKSPACE) for l in range(len(current_desc))] #to delete previous value
                name_zz_box.send_keys(description) #to add the new description
                admin_panel.save_provider()
                print(i, x + '\t' + description + '\t' + 'done - put in place' + '\t' + str(datetime.datetime.now()))
        except:
                print(f'Cannot assign description to provider {x}')





print("Done all done, closing chrome.")
driver.close()
