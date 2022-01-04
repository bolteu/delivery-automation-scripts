import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import re
import datetime
from utils.admin_panel import AdminPanel
from settings.config import username, password, chromedriver, base_admin_panel_url, old_base_admin_panel_url
from settings.config import js_dump, scope, doc_url
import os
#initialize model
creds = ServiceAccountCredentials.from_json_keyfile_dict(js_dump, scope) #initialise credentials for GSheet API
sheetname = os.path.basename(__file__) #get name of the current script and use it to find a list with same name in Gsheet file
client = gspread.authorize(creds) #Connect to API
spreadsheet = client.open_by_url(doc_url) #Open spreadsheet
database = spreadsheet.worksheet(sheetname) #Open the needed list
df = pd.DataFrame(database.get_all_records()).fillna('') #Read data for script
df.drop_duplicates(subset = df.columns[0], inplace = True) #make a distinct df with providers to avoid duplicates
print('Spreadsheet data from', sheetname, 'list has been read.')
driver = webdriver.Chrome(chromedriver) #Initialise driver from bin folder
admin_panel = AdminPanel(driver = driver)
admin_panel.login(username = username, password = password)
driver.maximize_window()  # makes it full screen
driver.implicitly_wait(50)
#execute
for i in range(len(df)):
    x = admin_panel.provider_url(df.iloc[i, 0])
    driver.get(x)
    driver.implicitly_wait(100)
    #version config
    button = driver.find_element_by_id('mui-component-select-version') #find version button
    time.sleep(2)
    driver.execute_script("arguments[0].scrollIntoView();", button)  # scroll down to the button
    curr_v = button.get_attribute('innerHTML') #get current version
    if "V2" in curr_v:
        print(i, x + '\t' + 'V2 has been already assigned' + '\t' + str(datetime.datetime.now())) #notify if V2 is already assigned
    else:
        button.click()  # click button
        driver.implicitly_wait(10)
        lst = driver.find_element_by_id('menu-version').find_elements_by_tag_name('li')
        for t in range(len(lst)):
            item = lst[t]
            driver.execute_script("arguments[0].scrollIntoView();", item)
            itemt = item.get_attribute('innerHTML')
            if 'V2' in itemt:
                item.click()
                time.sleep(1)
                print(i, x + '\t' + 'done - V2 assigned' + '\t' + str(datetime.datetime.now()))
                admin_panel.save_provider() #save only if v2 was assigned rn, if it was assigned before there is no this step
                break
    try: item.send_keys(Keys.ESCAPE)
    except: pass
print('All done! Closing chrome.')
driver.close()
