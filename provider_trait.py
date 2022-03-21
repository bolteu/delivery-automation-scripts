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
import json
import os

mode = input('Type in enable or disable: ') #Define if you want to add or remove

creds = ServiceAccountCredentials.from_json_keyfile_dict(js_dump, scope)
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
#Execution
for i in range(len(df)):
        x = admin_panel.provider_url(df.iloc[i, 0])
        driver.get(x)
        driver.implicitly_wait(100)
        #traits config
        button = driver.find_element_by_id('mui-component-select-traitSelector') #find traits button
        time.sleep(1.5)
        driver.execute_script("arguments[0].scrollIntoView();", button)  # scroll down to the button
        time.sleep(1.5)
        c_trt = button.get_attribute('innerHTML').replace('&amp;', '&') #get current trait
        c_trt_list = c_trt.split(sep = ', ')
        trt = str(df.iloc[i, 1])  # assign trait variable
        t_start = str(df.iloc[i, 2])  # trait start period variable
        t_stop = str(df.iloc[i, 3])  # trait stop period variable
        trt_re = trt.replace("(", "\(").replace(")", "\)")
        if trt_re in c_trt_list:
                if mode == 'enable':
                        if (t_start != '' and t_stop != ''):
                                driver.implicitly_wait(5)
                                sch_boxes = driver.find_elements_by_css_selector("div[ class *= 'scheduleButtonBox']")
                                for s in range(len(sch_boxes)):
                                        sch_box = driver.find_elements_by_css_selector("div[ class *= 'scheduleButtonBox']")[s]
                                        sch_name = sch_box.find_element_by_xpath('..').find_element_by_tag_name('p').get_attribute('innerHTML')
                                        sch_button = sch_box.find_element_by_tag_name('button')
                                        sch_block = sch_box.find_element_by_xpath('..').find_element_by_xpath('..')
                                        sch_forms = sch_block.find_elements_by_tag_name('input')
                                        if sch_name == trt:
                                                if len(sch_forms) == 0:
                                                        sch_button.click()
                                                time.sleep(1)
                                                sch_forms = sch_block.find_elements_by_tag_name('input')
                                                start_btn = sch_forms[0]
                                                driver.execute_script("arguments[0].scrollIntoView();", start_btn)  # scroll to for the schedule start field to be visible
                                                start_c_val = start_btn.get_attribute('value')
                                                [start_btn.send_keys(Keys.BACKSPACE) for b in range(len(start_c_val))]
                                                time.sleep(0.5)
                                                start_btn.send_keys(t_start)
                                                stop_btn = start_btn = sch_forms[1]
                                                stop_c_val = stop_btn.get_attribute('value')
                                                [stop_btn.send_keys(Keys.BACKSPACE) for b in range(len(start_c_val))]
                                                time.sleep(0.5)
                                                stop_btn.send_keys(t_stop)
                                                break
                                print(i, x + '\t' + c_trt + '\t' + 'was enabled before, recsheduled' + '\t' + str(datetime.datetime.now()))

                        else:
                                print(i, x + '\t' + c_trt + '\t' + 'was enabled before' + '\t' + str(datetime.datetime.now()))
                                continue
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
                        print(i, x + '\t' + c_trt + '\t' + 'done - disabled' + '\t' + str(datetime.datetime.now()))
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
                        #Scheduling config
                        if (t_start != '' and t_stop != ''):
                                driver.implicitly_wait(5)
                                sch_boxes = driver.find_elements_by_css_selector("div[ class *= 'scheduleButtonBox']")
                                for s in range(len(sch_boxes)):
                                        sch_box =  driver.find_elements_by_css_selector("div[ class *= 'scheduleButtonBox']")[s]
                                        sch_name = sch_box.find_element_by_xpath('..').find_element_by_tag_name('p').get_attribute('innerHTML')
                                        sch_button = sch_box.find_element_by_tag_name('button')
                                        if sch_name == trt:
                                                sch_button.click()
                                                time.sleep(1)
                                                per_fields = driver.find_elements_by_css_selector("div[class = 'react-datepicker-wrapper'")
                                                fld_counter = len(per_fields) #counts how many fields for start / stop periods we have
                                                start_btn =  per_fields[fld_counter - 2].find_element_by_tag_name('input')
                                                driver.execute_script("arguments[0].scrollIntoView();", start_btn)  # scroll to for the schedule start field to be visible
                                                start_btn.send_keys(t_start)
                                                stop_btn = per_fields[fld_counter - 1].find_element_by_tag_name('input')
                                                stop_btn.send_keys(t_stop)
                                                break
                        print(i, x + '\t' + c_trt + '\t' + 'done - enabled' + '\t' + str(datetime.datetime.now()))
                elif mode == 'disable':
                        print(i, x + '\t' + c_trt + '\t' + 'was disabled before' + '\t' + str(datetime.datetime.now()))
                        continue
        admin_panel.save_provider() #Save changes
print("Done all done, closing chrome.")
driver.close()
