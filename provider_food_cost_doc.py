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

for i in range(len(df)):
        x = admin_panel.provider_url(df.iloc[i, 0])
        param = str(df.iloc[i, 1])
        param_re = param.replace("(", "\(").replace(")", "\)")
        driver.get(x)
        driver.implicitly_wait(100)
        f_cost_button = driver.find_element_by_id('mui-component-select-should_send_client_food_cost_doc') #find f_cost button
        driver.execute_script("arguments[0].scrollIntoView();", f_cost_button)  # scroll down to the button
        time.sleep(1)
        f_cost_button.click()
        lst = driver.find_elements_by_xpath('//*[@id="menu-should_send_client_food_cost_doc"]/div[3]/ul/li[*]')
        for item in lst:
                item_c = item.get_attribute('innerHTML')
                item_c = re.findall("(.+?)<span", item_c)[0]
                if re.search(param_re, item_c):
                        item.click()
                else: continue
        time.sleep(1)
        admin_panel.save_provider() # Save changes
        print(x, round((i + 1) / len(df), 2), 'completed from total', datetime.datetime.now())
print("Done all done,  closing chrome.")
driver.close()
