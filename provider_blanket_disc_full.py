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
#code execution
for i in range(len(df)):
        x = admin_panel.provider_url(df.iloc[i, 0])
        #Read data for parameters to change
        new_com = str(df.iloc[i, 1])
        bl_disc = str(df.iloc[i, 2])
        n_p_com = str(df.iloc[i, 3])
        driver.get(x)
        time.sleep(1.5)
        driver.implicitly_wait(100)
        #Commission
        fee_box = driver.find_element(By.NAME, "amount")
        [fee_box.send_keys(Keys.BACKSPACE) for n in range(0,5)] #delete old, 5 backspaces for max 5 characters
        #add new
        time.sleep(1.5)
        fee_box.send_keys(new_com)
        #Blanket menu discount
        if mode == 'enable':
                bl_box = driver.find_element(By.NAME, "blanket_menu_discount_percentage")
                # delete old, 5 backspaces for max 5 characters
                [bl_box.send_keys(Keys.BACKSPACE) for n in range(0,5)]
                # add new
                bl_box.send_keys(bl_disc)
        elif mode == 'disable':
                pass
        #Tickbox
        time.sleep(1.5)
        bl_tick = driver.find_element(By.NAME, 'is_blanket_menu_discount_enabled')
        driver.execute_script("arguments[0].scrollIntoView();", bl_tick)
        if mode == 'enable':
                if bl_tick.is_selected() == True:
                        pass
                else:
                        bl_tick.click()
        if mode == 'disable':
                if bl_tick.is_selected() == True:
                        bl_tick.click()
                else:
                        pass
        driver.implicitly_wait(50)
        #Pickup commission
        if n_p_com == '': pass
        else:
                p_box = driver.find_element(By.NAME, "takeaway_amount") # find fee
                [p_box.send_keys(Keys.BACKSPACE) for n in range(0,5)] # check if fee is present - delete if needed
                time.sleep(1.5)
                p_box.send_keys(n_p_com) # new fee for pickup
        # traits config
        button = driver.find_element(By.ID, 'mui-component-select-traitSelector')  # find traits button
        time.sleep(1.5)
        driver.execute_script("arguments[0].scrollIntoView();", button)  # scroll down to the button
        time.sleep(1.5)
        c_trt = button.get_attribute('innerHTML')  # get current trait
        trt = 'Blanket campaign'  # assign trait variable
        trt_re = trt.replace("(", "\(").replace(")", "\)")
        driver.execute_script("arguments[0].scrollIntoView();", button)  # scroll down to the button
        if mode == 'enable':
                if re.search(trt_re, c_trt): pass
                else:
                        button.click()  # click button
                        driver.implicitly_wait(5)
                        lst = driver.find_elements(By.XPATH, '//*[@id="menu-traitSelector"]/div[3]/ul/li[*]')
                        for t in range(len(lst)):
                                item = driver.find_elements(By.XPATH, '//*[@id="menu-traitSelector"]/div[3]/ul/li[*]')[t]
                                driver.execute_script("arguments[0].scrollIntoView();", item)
                                itemt = item.get_attribute('innerHTML')
                                itemt = re.sub('<span.+', "", itemt)
                                if itemt == trt:
                                        item.click()
                                        time.sleep(1)
                                        item.send_keys(Keys.ESCAPE)
                                        break
        elif mode == 'disable':
                if re.search(trt_re, c_trt):
                        button.click()  # click button
                        driver.implicitly_wait(5)
                        lst = driver.find_elements(By.XPATH, '//*[@id="menu-traitSelector"]/div[3]/ul/li[*]')
                        for t in range(len(lst)):
                                item = driver.find_elements(By.XPATH, '//*[@id="menu-traitSelector"]/div[3]/ul/li[*]')[t]
                                driver.execute_script("arguments[0].scrollIntoView();", item)
                                itemt = item.get_attribute('innerHTML')
                                itemt = re.sub('<span.+', "", itemt)
                                if itemt == trt:
                                        item.click()
                                        time.sleep(1)
                                        item.send_keys(Keys.ESCAPE)
                                        break
                else: pass
        driver.implicitly_wait(5)
        admin_panel.save_provider() # Save changes
        print(x, round((i + 1) / len(df), 2), 'completed from total', datetime.datetime.now())
print("Done all done, closing chrome.")
driver.close()