import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import re
import datetime
from utils.admin_panel import AdminPanel
from utils.driver import driver
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

admin_panel = AdminPanel(driver = driver)
admin_panel.login(username = username, password = password)
driver.maximize_window()  # makes it full screen

for i in range(len(df)):
        x = admin_panel.provider_url(df.iloc[i, 0])
        mode = str(df.iloc[i, 1])
        driver.get(x)
        time.sleep(1)
        driver.implicitly_wait(100)
        ml_box = driver.find_element_by_name('disable_estimation_correction')
        ml_param = ml_box.find_element_by_xpath('..').find_element_by_xpath('..').get_attribute('class')
        if re.search('checked', ml_param):
                if mode == 'enable':
                        continue
                else:
                        ml_box.click()
        else:
                if mode == 'enable':
                        ml_box.click()
                else:
                        continue
        # Save changes
        admin_panel.save_provider()
        print(x, round((i + 1) / len(df), 2), 'completed from total', datetime.datetime.now())
print("Done all done, closing chrome.")
driver.close()

