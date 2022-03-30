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
        x = admin_panel.provider_url(df.iloc[i, 0])
        cols = df.columns.values.tolist()  # Get column titles
        driver.get(x) #open provider url
        driver.implicitly_wait(10)
        pc_box = driver.find_element_by_name('is_promotion_enabled') #Find Promotions checkbox element
        time.sleep(1)
        driver.execute_script("arguments[0].scrollIntoView();", pc_box)  # Scroll down to the button
        promo_param = pc_box.find_element_by_xpath('..').find_element_by_xpath('..').get_attribute('class')
        if re.search('checked', promo_param):
                if mode == 'enable': pass
                elif mode == 'disable': pc_box.click()
        else:
                if mode == 'enable': pc_box.click()
                elif mode == 'disable': pass
        driver.implicitly_wait(10)
        promo_block = driver.find_element_by_xpath("// p[contains(text(), 'Promotions')]").find_element_by_xpath('..')
        p_boxes = promo_block.find_elements_by_css_selector("div[style *= 'grid-column:']")
        for p in range(len(p_boxes)):
                if p == 0: continue
                p_label = p_boxes[p].find_element_by_tag_name('label').get_attribute('innerHTML')
                i_form = p_boxes[p].find_elements_by_tag_name('textarea')[0]
                for c in range(len(cols)):
                        col_name = cols[c]
                        if c == 0: continue  # skip first column data
                        desc = str(df.iloc[i, c])
                        if col_name == p_label:
                                # remove old
                                i_form_v = i_form.get_attribute('innerHTML')
                                [i_form.send_keys(Keys.BACKSPACE) for f in range(len(i_form_v))]
                                if mode == 'enable':  i_form.send_keys(desc) # enter new
                                elif mode == 'disable': pass
        admin_panel.save_provider() # Save changes
        print(x, round((i + 1) / len(df), 2), 'completed from total', datetime.datetime.now())
print("Done all done, closing chrome.")
driver.close()