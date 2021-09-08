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
from settings.config import scope, doc_url, js_dump, json_credentials
import json
import os

with open(json_credentials, 'w') as fp: json.dump(js_dump, fp, indent = 2) #create a dump of json credentials

creds = ServiceAccountCredentials.from_json_keyfile_name(json_credentials, scope) #initialise credentials for GSheet API
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

print(( 'x' + '\t' + 'TIMESTAMP' + '\t' + 'old_fee' + '\t' + 'new_fee' + '\t' + 'Done'))

for i in range(len(df)):
        x = base_admin_panel_url + "/delivery/providers/" + str(df.iloc[i, 0])
        n_mov = str(df.iloc[i, 1])
        driver.get(x)
        time.sleep(1.5)
        driver.implicitly_wait(100)
        mov_box = driver.find_element_by_name('min_order_price')
        mov_c = mov_box.get_attribute('value') #get_MOV
        #get MOV_len
        [mov_box.send_keys(Keys.BACKSPACE) for n in range(len(mov_c))] # remove old fee
        time.sleep(1)
        mov_box.send_keys(n_mov) #add new fee
        # Save changes
        admin_panel.save_provider(driver)
        print( x + '\t' + str(datetime.datetime.now()) + '\t' + mov_c + '\t' + n_mov + '\t' + 'Done')
print("Done all done, removing credentials file & closing chrome.")
os.remove(json_credentials)
driver.close()
