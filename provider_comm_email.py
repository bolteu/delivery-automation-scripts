import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
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
driver = webdriver.Chrome(chromedriver) #Initialise driver from bin folder
admin_panel = AdminPanel(driver = driver)
admin_panel.login(username = username, password = password)
driver.maximize_window()  # makes it full screen
#Automation execution
for i in range(len(df)):
    comm_email = str(df.iat[i, 1])
    x = base_admin_panel_url + "/delivery/providers/" + str(df.iat[i, 0])
    driver.get(x) #open provider profile in admin
    time.sleep(2) #wait a bit for the values in all forms to load
    driver.implicitly_wait(10) #timeout waiting step
    c_email_box = driver.find_element(By.NAME,'communication_email')  # locate element where the comm email is stored
    driver.execute_script("arguments[0].scrollIntoView();", c_email_box) #scroll page to the element to interact with it
    c_email_val = c_email_box.get_attribute('value') #get current value of comm email
    [c_email_box.send_keys(Keys.BACKSPACE) for c in range(len(c_email_val))] #remove old comm email
    time.sleep(1)
    c_email_box.send_keys(comm_email) #add new comm email (from database)
    admin_panel.save_provider() #save changes block
    print(x, round((i + 1) / len(df), 2), 'completed from total', datetime.datetime.now())
print("Done all done, closing chrome.")
driver.close()
