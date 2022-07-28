# This Python file uses the following encoding: utf-8

# In case of any questions contact: krzysztof.witkowski@bolt.eu
from time import sleep
from selenium import webdriver
import pandas as pd
from utils.driver import driver
from utils.admin_panel import AdminPanel
from utils.get_cell_value import get_cell_value
from settings.config import username, password, database, chromedriver, base_admin_panel_url
import re
from selenium.webdriver.common.by import By

df = pd.read_csv(database)

driver.maximize_window()
columns = list(df)
total_lines = len(list(df.iterrows()))

admin_panel = AdminPanel(driver=driver)

# ​ Admin-panel login
admin_panel.login(username=username, password=password)

couriers_not_registered = []
script_step = ''
extra_step_info = []

for index, row in df.iterrows():
    extra_step_info = []
    print("{index} / {total_lines} - {phone_number}".format(index=index+1, total_lines=total_lines, phone_number=get_cell_value(row, "partner_phone")), end="")
    try:
        script_step = 'create partner profile'
        driver.implicitly_wait(3)
        # partner profile:
        driver.get(base_admin_panel_url + "/fleet-root/partners/new")
        # create partner profile:
        for column in columns:
            if "partner" in column:
                #input(str(column) + ":" + str(get_cell_value(row, column)))
                field_name = column.replace("partner_", "")
                admin_panel.set_form_value(field_name, get_cell_value(row, column))
        driver.find_element(By.XPATH, "//span[contains(text(),'Save')]").click()
        sleep(1)
        driver.implicitly_wait(10)

        admin_panel.wait_for_url_change('partners/edit/\d+')

        url = driver.current_url
        extra_step_info.append('Partner profile: ' + url)
        pattern = 'edit/(\d+)'
        id = re.search(pattern, url)[1]
        script_step = 'create courier profile'
        partner_url = base_admin_panel_url + "/delivery-courier/partners/" + str(id) + "/couriers/create"
        driver.get(partner_url)

        # driver.find_element_by_link_text("Create").click()
        driver.implicitly_wait(10)

        # create courier profile:
        for column in columns:
            if "courier_" in column:
                #input(str(column) + ":" + str(get_cell_value(row, column)))
                field_name = column.replace("courier_","")
                admin_panel.set_form_value(field_name, get_cell_value(row, column))
        driver.find_element(By.XPATH, "//span[contains(text(),'Save')]").click()

        admin_panel.wait_for_url_change('couriers/\d+\?tab=COURIER')

        script_step = 'Add bag info'
        courier_id = re.search("([0-9]+)", driver.current_url)[0]
        extra_step_info.append('Courier profile id: ' + courier_id)
        driver.get(f'{admin_panel.courier_url(courier_id)}?tab=BAGS')
        sleep(1)

        for column in columns:
            if 'bag_' in column:
                if column == 'bag_serial':
                    field_name = 'bagSerial'
                else:
                    field_name = column.replace('bag_', '')
                admin_panel.set_form_value(field_name, get_cell_value(row, column))
        bag_assign_el = driver.find_element(By.XPATH, "//span[contains(text(),'Assign Bag')]")
        bag_assign_el = bag_assign_el.find_element(By.XPATH, "..").click()
        if 'force_confirmation_bag' in columns:
            if get_cell_value(row, 'force_confirmation_bag') == 1:
                bag_assign_confirmation = driver.find_element(By.XPATH, "//span[contains(text(),'Ok')]")
                bag_assign_confirmation.find_element(By.XPATH, "..").click()
        sleep(1)
        print(" [OK]")
    except:
        print(" [FAILED]")
        details = admin_panel.collect_page_errors() or (extra_step_info + [script_step + " error"])
        couriers_not_registered.append((get_cell_value(row, "partner_phone"), details))

driver.close()

if not couriers_not_registered:
    print("All couriers registered correctly.")
else:
    print("Phone numbers of not registered couriers:")
    for failed_item in couriers_not_registered:
        print(failed_item[0])
        print("\n".join(failed_item[1]))
        print()