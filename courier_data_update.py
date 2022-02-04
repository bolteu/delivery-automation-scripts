# This Python file uses the following encoding: utf-8
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from utils.admin_panel import AdminPanel, get_element_type
from utils.get_cell_value import get_cell_value
from settings.config import username, password, database, chromedriver, base_admin_panel_url
from selenium.webdriver.common.keys import Keys
import re

df = pd.read_csv(database)
driver = webdriver.Chrome(chromedriver)
driver.maximize_window()
columns = list(df)
total_lines = len(list(df.iterrows()))

admin_panel = AdminPanel(driver=driver)

# ​ Admin-panel login
admin_panel.login(username=username, password=password)

couriers_not_updated = []
script_step = ''
extra_step_info = []

for index, row in df.iterrows():
    extra_step_info = []
    courier_id = row.courier_id
    print("{index} / {total_lines} - {courier_id}".format(index=index+1, total_lines=total_lines, courier_id=courier_id, end=""))

    try:
        script_step = 'update courier'
        driver.implicitly_wait(20)
        # courier profile:
        driver.get(base_admin_panel_url + "/delivery-courier/couriers/" + str(courier_id))
        # update courier profile:
        for column in columns:
            if column == 'courier_id': continue
            el = driver.find_element(By.NAME, column)
            el_type = get_element_type(el)
            if el_type == "text":
                sleep(3)
                [el.send_keys(Keys.BACKSPACE) for i in range(len(el.get_attribute('value')))]
            admin_panel.set_form_value(column, get_cell_value(row, column))

        driver.find_element(By.XPATH, "//span[contains(text(),'Save')]").click()
        sleep(2.5)
        driver.implicitly_wait(10)
        print("[OK]Courier " + str(courier_id) + " data updated ")
    except:
        print("[FAILED]")
        details = admin_panel.collect_page_errors() or (extra_step_info + [script_step + " error"])
        couriers_not_updated.append((courier_id, details))

driver.close()

if not couriers_not_updated:
    print("All couriers have been updated correctly.")
else:
    print("Ids of not updated couriers:")
    for failed_item in couriers_not_updated:
        print(failed_item[0])
        print("\n".join(failed_item[1]))
        print()