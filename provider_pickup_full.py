import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import re
import datetime
from utils.admin_panel import AdminPanel
from settings.config import username, password, database, chromedriver, base_admin_panel_url, old_base_admin_panel_url
from settings.config import scope, doc_url, js_dump
import json
import os

mode = input('Type in enable or disable: ') #Define if you want to add or remove

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

#Execution
for i in range(len(df)):
        x = admin_panel.provider_url(df.iloc[i, 0])
        driver.get(x)
        time.sleep(2)
        driver.implicitly_wait(100)
        pickup_box = driver.find_element_by_name("is_accepting_takeaway_orders") #locate pickup box
        pickup_param = pickup_box.find_element_by_xpath('..').find_element_by_xpath('..').get_attribute('class') # Pickup - check if enabled
        if mode == 'enable':
                if re.search('checked', pickup_param): pass
                else: pickup_box.click() #enable pickup if it is not enabled
        elif mode == 'disable':
                if re.search('checked', pickup_param): pickup_box.click()
                else: pass #disable enable pickup if it is not disabled enabled
        driver.implicitly_wait(100)
        pf_box = driver.find_element_by_name("takeaway_amount") #find pickup fee element
        pickup_fee = pf_box.get_attribute('value') #get current pickup fee value
        [pf_box.send_keys(Keys.BACKSPACE) for n in range(len(pickup_fee))] #remove old fee
        time.sleep(1)
        driver.find_element_by_name("takeaway_amount").send_keys(str(df.iloc[i, 1]))# Insert new pickup fee
        # Save changes
        admin_panel.save_provider()
        print(x, round((i + 1) / len(df), 2), 'completed from total', datetime.datetime.now())
print("Done all done, closing chrome.")
driver.close()


