import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
mode = input('Type in enable or disable: ') #Define if you want to add or remove
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
        driver.get(x)
        driver.implicitly_wait(100)
        #tags config
        tag_button = driver.find_element(By.ID, 'mui-component-select-tag_ids') #find tags button
        time.sleep(2)
        driver.execute_script("arguments[0].scrollIntoView();", tag_button)  # scroll down to the button
        time.sleep(1)
        c_tag = tag_button.get_attribute('innerHTML').replace('&amp;', '&') #get current trait
        tag = str(df.iloc[i, 1])  # assign tag variable
        tag_re = tag.replace("(", "\(").replace(")", "\)")
        if re.search(tag_re, c_tag):
                if mode == 'enable':
                        print(i, x + '\t' + c_tag + '\t' + 'was enabled before' + '\t' + str(datetime.datetime.now()))
                        continue
                elif mode == 'disable':
                        tag_button.click()  # click button
                        driver.implicitly_wait(10)
                        lst = driver.find_element(By.ID, 'menu-tag_ids').find_elements(By.TAG_NAME, 'li')
                        for t in range(len(lst)):
                                item = driver.find_element(By.ID, 'menu-tag_ids').find_elements(By.TAG_NAME, 'li')[t]
                                driver.execute_script("arguments[0].scrollIntoView();", item)
                                itemt = item.get_attribute('innerHTML').replace('&amp;', '&')
                                itemt = re.sub('<span.+', "", itemt)
                                if itemt == tag:
                                        item.click()
                                        time.sleep(1)
                                        item.send_keys(Keys.ESCAPE)
                                        break
                                else: continue
                        try: item.send_keys(Keys.ESCAPE)
                        except: pass
                        print(i, x + '\t' + c_tag + '\t' + 'done - disabled' + '\t' + str(datetime.datetime.now()))
        else:
                if mode == 'enable':
                        tag_button.click()  # click button
                        driver.implicitly_wait(10)
                        lst = driver.find_element(By.ID, 'menu-tag_ids').find_elements(By.TAG_NAME, 'li')
                        for t in range(len(lst)):
                                item = driver.find_element(By.ID, 'menu-tag_ids').find_elements(By.TAG_NAME, 'li')[t]
                                driver.execute_script("arguments[0].scrollIntoView();", item)
                                itemt = item.get_attribute('innerHTML').replace('&amp;', '&')
                                itemt = re.sub('<span.+', "", itemt)
                                if itemt == tag:
                                        item.click()
                                        time.sleep(1)
                                        item.send_keys(Keys.ESCAPE)
                                        break
                                else: continue
                        try: item.send_keys(Keys.ESCAPE)
                        except: pass
                        print(i, x + '\t' + c_tag + '\t' + 'done - enabled' + '\t' + str(datetime.datetime.now()))
                elif mode == 'disable':
                        print(i, x + '\t' + c_tag + '\t' + 'was disabled before' + '\t' + str(datetime.datetime.now()))
                        continue
        admin_panel.save_provider()
print("Done all done, closing chrome.")
driver.close()