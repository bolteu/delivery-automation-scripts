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

mode = input('Type in enable or disable: ') #Define if you want to add or remove

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
#code execution
for i in range(len(df)):
        x = base_admin_panel_url + "/delivery/providers/" + str(df.iloc[i, 0])
        #Read data for parameters to change
        new_com = str(df.iloc[i, 1])
        bl_disc = str(df.iloc[i, 2])
        n_p_com = str(df.iloc[i, 3])
        driver.get(x)
        driver.implicitly_wait(100)
        #Commission
        fee_box = driver.find_element_by_name("amount")
        c_fee = driver.find_element_by_name("amount").get_attribute('value')
        while len(c_fee) == 0:
                fee_box = driver.find_element_by_name("amount")
                c_fee = driver.find_element_by_name("amount").get_attribute('value')
        [fee_box.send_keys(Keys.BACKSPACE) for n in range(len(c_fee))] #delete old
        #add new
        time.sleep(1.5)
        fee_box.send_keys(new_com)
        #Blanket menu discount
        if mode == 'enable':
                bl_box = driver.find_element_by_name("blanket_menu_discount_percentage")
                bl_am = bl_box.get_attribute('value')
                while len(bl_am) == 0:
                        bl_box = driver.find_element_by_name("blanket_menu_discount_percentage")
                        bl_am = bl_box.get_attribute('value')
                # delete old
                [bl_box.send_keys(Keys.BACKSPACE) for n in range(len(bl_am))]
                # add new
                bl_box.send_keys(bl_disc)
        elif mode == 'disable':
                pass
        #Tickbox
        time.sleep(1.5)
        bl_tick = driver.find_element_by_name('is_blanket_menu_discount_enabled')
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
                p_box = driver.find_element_by_name("takeaway_amount") # find fee
                pickup_fee = p_box.get_attribute('value') # get pickup fee value
                while len(pickup_fee) == 0:
                        p_box = driver.find_element_by_name("takeaway_amount")  # find fee
                        pickup_fee = p_box.get_attribute('value')  # get pickup fee value
                [p_box.send_keys(Keys.BACKSPACE) for n in range(len(pickup_fee))] # check if fee is present - delete if needed
                time.sleep(1.5)
                p_box.send_keys(n_p_com) # new fee for pickup
        # traits config
        button = driver.find_element_by_id('mui-component-select-traitSelector')  # find traits button
        time.sleep(1.5)
        driver.execute_script("arguments[0].scrollIntoView();", button)  # scroll down to the button
        time.sleep(1.5)
        c_trt = button.get_attribute('innerHTML')  # get current trait
        trt = 'Blanket campaign'  # assign trait variable
        trt_re = trt.replace("(", "\(").replace(")", "\)")
        if c_trt == '<span>​</span>': c_trt == ""
        driver.execute_script("arguments[0].scrollIntoView();", button)  # scroll down to the button
        if mode == 'enable':
                if re.search(trt_re, c_trt): pass
                else:
                        button.click()  # click button
                        driver.implicitly_wait(5)
                        lst = driver.find_elements_by_xpath('//*[@id="menu-traitSelector"]/div[3]/ul/li[*]')
                        for t in range(len(lst)):
                                item = driver.find_elements_by_xpath('//*[@id="menu-traitSelector"]/div[3]/ul/li[*]')[t]
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
                        lst = driver.find_elements_by_xpath('//*[@id="menu-traitSelector"]/div[3]/ul/li[*]')
                        for t in range(len(lst)):
                                item = driver.find_elements_by_xpath('//*[@id="menu-traitSelector"]/div[3]/ul/li[*]')[t]
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