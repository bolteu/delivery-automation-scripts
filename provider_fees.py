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
    url = base_admin_panel_url + "/delivery/providers/" + str(df.iloc[i, 0])  + "?tab=fees"
    fee_type = str(df.iloc[i,1])
    driver.get(url)
    driver.implicitly_wait(10)
    add_fee_button = driver.find_element_by_xpath("// span[contains(text(), 'Add a new fee')]") # find Add fee button
    driver.execute_script("arguments[0].click();", add_fee_button) #click add fee button
    time.sleep(1) #wait for the form's elements to appear
    driver.implicitly_wait(10)
    fee_form = driver.find_elements_by_tag_name('form')[0] # find all forms that a provider has, choose the newly created one to edit
    fee_type_block = fee_form.find_element_by_name("fee_type").find_element_by_xpath('..') # find fee type block
    fee_type_block.click() #click fee type block
    fee_dropdown = driver.find_element_by_css_selector("ul[role = 'listbox']") #find dropdown of fee types
    fee_types = fee_dropdown.find_elements_by_tag_name('li') #find options of the dropdown
    #Iterate through the list of options to click the right one (based on input data)
    for f in range(len(fee_types)):
        fee_el = fee_dropdown.find_elements_by_tag_name('li')[f] #find element
        fee_t = fee_el.get_attribute('innerHTML') #read inner html to get the name
        fee_t = fee_t[0:fee_t.find('<')] #remove irrelevant html
        if fee_t == fee_type: #check if fee type from dropdown matches the one in CSV
            fee_el.click() # click if yes
    time.sleep(4)  # wait for the updated form's elements to appear
    # populate fields with data
    field_grid = fee_form.find_elements_by_css_selector("div[style *= 'grid-template-columns']")[1]  # locate grid with data fields on the fee
    fee_fields  = field_grid.find_elements_by_tag_name('input')
    for ff in range(len(fee_fields)):
        ff_el = field_grid.find_elements_by_tag_name('input')[ff].find_element_by_xpath('..').find_element_by_xpath('..')
        ff_label = ff_el.find_element_by_tag_name('label').get_attribute('innerHTML') # get label element inner html to extract label name from there
        ff_label = re.sub('<span.+', '', ff_label) #get label name of the form to match it with column name to add data to the correct form
        ff_label = ff_label.replace('&nbsp;', '')
        ff_input = ff_el.find_element_by_tag_name('input') #find input form to put data there
        [ff_input.send_keys(Keys.BACKSPACE) for fff in range(0,16)]  # delete dummy (default values) in input forms, deletes 16 characters irrespectively of the contained data
        # 16 characters as the date variable is the longest one to delete and it has 16 characters
        ff_input.send_keys(str(df.loc[i, ff_label])) #add values from CSV (based on column names, they need to match forms' names
    admin_panel.save_provider() #save fees data
    print(url, round((i + 1) / len(df), 2), 'completed from total', datetime.datetime.now()) #show progress of the code's execution to the user
print("Done all done, closing chrome.")
driver.close()
