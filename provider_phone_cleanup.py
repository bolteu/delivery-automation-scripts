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
import random
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
#Automation execution
for i in range(len(df)):
    dummy_phone = str(random.randint(1, 10)) # test line to see if phones are saved after the code is executed
    url = admin_panel.provider_url(df.iloc[i, 0]) #define link to provider in admin
    driver.get(url) #open provider profile in admin
    time.sleep(1.5) #wait a bit for the values in all forms to load
    driver.implicitly_wait(10) #timeout waiting step
    phone_box = driver.find_element(By.NAME, 'phone') #locate element where provider phone is stored
    driver.execute_script("arguments[0].scrollIntoView();", phone_box) #scroll page to the element to interact with it
    c_email_val = phone_box.get_attribute('value') #get current value of phone
    [phone_box.send_keys(Keys.BACKSPACE) for c in range(len(c_email_val))] #remove old phone
    time.sleep(1)
    phone_box.send_keys(dummy_phone) #add new phone
    admin_panel.save_provider()  # save fees data
    print(url, round((i + 1) / len(df), 2), 'completed from total', datetime.datetime.now()) #show progress of the code's execution to the user
print("Done all done, closing chrome.")
driver.close()