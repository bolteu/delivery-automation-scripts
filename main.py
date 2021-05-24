# This Python file uses the following encoding: utf-8

# In case of any questions contact: krzysztof.witkowski@bolt.eu
from time import sleep
from selenium import webdriver
import pandas as pd
from utils.admin_panel import AdminPanel
from utils.get_cell_value import get_cell_value
from settings.config import username, password, database, chromedriver, base_admin_panel_url
import re

df = pd.read_csv(database)
driver = webdriver.Chrome(chromedriver)
columns = list(df)

admin_panel = AdminPanel(driver=driver)

# ​ Admin-panel login
admin_panel.login(username=username, password=password)

couriers_not_registered = []

for index, row in df.iterrows():
    try:
        driver.implicitly_wait(3)
        #sleep(2)
        # partner profile:
        driver.execute_script("window.open('" + base_admin_panel_url + "/fleet-root/partners/new')")
        # courier profile admin panel:
        # driver.execute_script("window.open('" + base_admin_panel_url + "/delivery/partners/1627816/couriers/create')")
        # driver.implicitly_wait(3)
        driver.switch_to.window(driver.window_handles[index + 1])
        url = driver.current_url
        print(url)
        # create partner profile:
        for column in columns:
            if "partner" in column:
                # If you want to debug - you can use next trick
                #input(str(column) + ":" + str(get_cell_value(row, column)))
                field_name = column.replace("partner_", "")
                admin_panel.set_form_value(field_name, get_cell_value(row, column))
        driver.find_element_by_xpath("//span[contains(text(),'Save')]").click()
        sleep(1)
        driver.implicitly_wait(10)


        url = driver.current_url
        print(url)
        pattern = 'edit/(\d+)'
        id = re.search(pattern, url)[1]
        print("ID:")
        print(id)
        partner_url = base_admin_panel_url + "/delivery/delivery/partners/" + str(id) + "/couriers/create"
        print("URL:")
        print(partner_url)
        # input(str(column) + ":" + str(get_cell_value(row, column)))
        driver.get(partner_url)

        # driver.find_element_by_link_text("Create").click()
        driver.implicitly_wait(10)

        # create courier profile:
        for column in columns:
            if "courier_" in column:
                #input(str(column) + ":" + str(get_cell_value(row, column)))
                field_name = column.replace("courier_","")
                admin_panel.set_form_value(field_name, get_cell_value(row, column))
        driver.find_element_by_xpath("//span[contains(text(),'Save')]").click()
    except:
        couriers_not_registered.append(get_cell_value(row, "partner_phone"))

if not couriers_not_registered:
    print("All couriers registered correctly.")
else:
    print("Phone numbers of not registered couriers:")
    print(couriers_not_registered)

    # except Exception as e:
    #     couriers_not_registered.append(get_cell_value(row, "partner_phone"))
    #     # print("Courier not registered: ")
    #     # print(e)
    #     # input("Press enter to continue")
test = 0