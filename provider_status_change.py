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
import os




creds = ServiceAccountCredentials.from_json_keyfile_dict(js_dump, scope) #initialise credentials for GSheet API
sheetname = os.path.basename(__file__) #get name of the current script and use it to find a list with same name in Gsheet file
client = gspread.authorize(creds) #Connect to API
spreadsheet = client.open_by_url(doc_url) #Open spreadsheet
database = spreadsheet.worksheet(sheetname) #Open the needed list
df = pd.DataFrame(database.get_all_records()).fillna('') #Read data for script
print('Spreadsheet data from', sheetname, 'list has been read.')
driver = webdriver.Chrome(service = chromedriver) #Initialise driver from bin folder
admin_panel = AdminPanel(driver = driver)
admin_panel.login(username = username, password = password)
driver.maximize_window()  # makes it full screen
time.sleep(1)



for i in range(len(df)):
        x = admin_panel.provider_url(df.iloc[i, 0]) + "?tab=status"
        driver.get(x)
        driver.implicitly_wait(100)
        #status config
        status_button = driver.find_element_by_id('mui-component-select-status') #find status button
        time.sleep(2)
        driver.execute_script("arguments[0].scrollIntoView();", status_button)  # scroll down to the button
        time.sleep(1)
        c_status = status_button.get_attribute('innerHTML').replace('&amp;', '&') #get current commission
        status = str(df.iloc[i, 1])  # assign status variable
        status_re = status.replace("(", "\(").replace(")", "\)")
        if re.search(status_re, c_status):

                print(i, x + '\t' + c_status + '\t' + 'was in place before' + '\t' + str(datetime.datetime.now()))
        else:
                status_button.click()  # click button
                driver.implicitly_wait(10)
                lst = driver.find_element_by_id('menu-status').find_elements_by_tag_name('li')
                for t in range(len(lst)):
                        item = driver.find_element_by_id('menu-status').find_elements_by_tag_name('li')[t]
                        driver.execute_script("arguments[0].scrollIntoView();", item)
                        itemt = item.get_attribute('innerHTML').replace('&amp;', '&')
                        itemt = re.sub('<span.+', "", itemt)
                        if itemt == status:
                                item.click()
                                time.sleep(1)
                                break
                        else: continue
                try: item.send_keys(Keys.ESCAPE)
                except: pass
                print(i, x + '\t' + status + '\t' + 'done - put in place' + '\t' + str(datetime.datetime.now()))

                admin_panel.save_provider()
print("Done all done, closing chrome.")
driver.close()

    
    
    
    
    
    
    