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
#Code execution
for i in range(len(df)):
        x = admin_panel.provider_url(df.iloc[i, 0])
        cols = df.columns.values.tolist()  # Get column titles
        driver.get(x) #open provider url
        driver.implicitly_wait(20)
        c_setup = driver.find_element(By.XPATH, "// p[contains(text(), 'Courier setup')]").find_element(By.XPATH, "..") #find courier notes section
        time.sleep(3.5) #wait for elements' values to load: change this value to a higher in case of problems
        for c in cols[1:]:
                field = c_setup.find_element(By.NAME, c)
                [field.send_keys(Keys.BACKSPACE) for i in range(len(field.get_attribute('innerHTML')))] #remove old
                field.send_keys(df.loc[i, c]) # add new
        admin_panel.save_provider() # Save changes
        print(x, round((i + 1) / len(df), 2), 'completed from total', datetime.datetime.now())
print("Done all done, closing chrome.")
driver.close()