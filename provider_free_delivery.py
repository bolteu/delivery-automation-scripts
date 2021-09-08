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

mode = input('Type in enable or disable: ') #Define if you want to add or remove

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

for i in range(len(df)):
        x = base_admin_panel_url + "/delivery/providers/" + str(df.iloc[i, 0])
        driver.get(x)
        #Initiate variables
        bd_fee = str(df.iloc[i, 1])
        b_dist = str(df.iloc[i, 2])
        reg_fee = str(df.iloc[i, 3])
        camp_fee = str(df.iloc[i, 4])
        trt = str(df.iloc[i, 5])
        trt_re = trt.replace("(", "\(").replace(")", "\)")
        # Delivery fee
        time.sleep(1)
        del_box = driver.find_element_by_name('client_delivery_min_price')
        driver.execute_script("arguments[0].scrollIntoView();", del_box)
        del_val = del_box.get_attribute('value')
        [del_box.send_keys(Keys.BACKSPACE) for n in range(len(del_val))] # delete old
        time.sleep(1)
        del_box.send_keys(bd_fee) # add new
        # Del. distance
        time.sleep(1)
        dd = driver.find_element_by_name('client_delivery_min_price_distance_in_km')
        driver.execute_script("arguments[0].scrollIntoView();", dd)
        dd_val = dd.get_attribute('value')
        [dd.send_keys(Keys.BACKSPACE) for n in range(len(dd_val))] # delete old
        time.sleep(1)
        dd.send_keys(b_dist) # add new
        #Commission
        time.sleep(1)
        fee_b = driver.find_element_by_name('amount')
        driver.execute_script("arguments[0].scrollIntoView();", fee_b)
        fee_val = fee_b.get_attribute('value')
        [fee_b.send_keys(Keys.BACKSPACE) for n in range(len(fee_val))] # delete old
        time.sleep(1)
        if mode == 'enable': fee_b.send_keys(camp_fee) # add new fee when enabling free delivery
        elif mode == 'disable': fee_b.send_keys(reg_fee)  # add new fee when disabling free delivery
        # traits config
        button = driver.find_element_by_id('mui-component-select-traitSelector')  # find traits button
        time.sleep(2)
        driver.execute_script("arguments[0].scrollIntoView();", button)  # scroll down to the button
        time.sleep(1)
        c_trt = button.get_attribute('innerHTML').replace('&amp;', '&')  # get current trait
        trt = str(df.iloc[i, 5])  # assign trait variable
        trt_re = trt.replace("(", "\(").replace(")", "\)")
        if c_trt == '<span>​</span>': c_trt == ""
        if trt == '': pass
        else:
                if re.search(trt_re, c_trt):
                        if mode == 'enable':
                                pass
                        elif mode == 'disable':
                                button.click()  # click button
                                driver.implicitly_wait(10)
                                lst = driver.find_element_by_id('menu-traitSelector').find_elements_by_tag_name('li')
                                for t in range(len(lst)):
                                        item = driver.find_element_by_id('menu-traitSelector').find_elements_by_tag_name('li')[t]
                                        driver.execute_script("arguments[0].scrollIntoView();", item)
                                        itemt = item.get_attribute('innerHTML').replace('&amp;', '&')
                                        itemt = re.sub('<span.+', "", itemt)
                                        if itemt == trt:
                                                item.click()
                                                time.sleep(1)
                                                item.send_keys(Keys.ESCAPE)
                                                break
                                try: item.send_keys(Keys.ESCAPE)
                                except: pass
                else:
                        if mode == 'enable':
                                button.click()  # click button
                                driver.implicitly_wait(10)
                                lst = driver.find_element_by_id('menu-traitSelector').find_elements_by_tag_name('li')
                                for t in range(len(lst)):
                                        item = driver.find_element_by_id('menu-traitSelector').find_elements_by_tag_name('li')[t]
                                        driver.execute_script("arguments[0].scrollIntoView();", item)
                                        itemt = item.get_attribute('innerHTML').replace('&amp;', '&')
                                        itemt = re.sub('<span.+', "", itemt)
                                        if itemt == trt:
                                                item.click()
                                                time.sleep(1)
                                                item.send_keys(Keys.ESCAPE)
                                                break
                                try: item.send_keys(Keys.ESCAPE)
                                except: pass
                        elif mode == 'disable':
                                pass
        # Save changes
        admin_panel.save_provider(driver)
        print(x, round((i + 1) / len(df), 2), 'completed from total', datetime.datetime.now())
print("Done all done, removing credentials file & closing chrome.")
os.remove(json_credentials)
driver.close()