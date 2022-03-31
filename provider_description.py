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
        x = admin_panel.provider_url(df.iloc[i, 0]) #define link to provider
        driver.get(x) #open provider
        cols = df.columns.values.tolist()  # Get column titles
        driver.implicitly_wait(10)
        b_info = driver.find_element_by_xpath("// p[contains(text(), 'Basic information')]") #find Basic information label
        b_info = b_info.find_element_by_xpath('..') #find Basic information block
        time.sleep(1) #wait for elemenents to load
        for c in range(len(cols)):
                col_name = cols[c] #define column name
                if c == 0: continue  #skip first column data because it is provider id
                desc = str(df.iloc[i, c]) #define descrption variable
                desc_label = driver.find_element_by_xpath("// label[contains(text()," + "'" + col_name + "'" + ")]") #find description bloc
                desc_box  = desc_label.find_element_by_xpath('..') #find box with description
                desc_input = desc_box.find_elements_by_tag_name('textarea')[0] #find text area to enter text
                c_desc = desc_input.get_attribute('innerHTML') #get current description
                [desc_input.send_keys(Keys.BACKSPACE) for l in range(len(c_desc))] #remove current description if it is present
                time.sleep(0.5) #wait a bit before entering a new description
                desc_input.send_keys(desc) #enter new description
        admin_panel.save_provider() # Save changes
        print(x, round((i + 1) / len(df), 2), 'completed from total', datetime.datetime.now())
print("Done all done, closing chrome.")
driver.close()