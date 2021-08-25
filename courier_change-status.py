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
    new_courier_status = row.courier_status

    print("{index} / {total_lines} - {courier_id}".format(index=index+1, total_lines=total_lines, courier_id=courier_id, end=""))

    try:
        script_step = 'change status'
        driver.implicitly_wait(3)
        driver.get(base_admin_panel_url + "/delivery-courier/couriers/" + courier_id)

        admin_panel.set_form_value(column, new_courier_status)

        driver.find_element_by_xpath("//span[contains(text(),'Save')]").click()
        sleep(1)

        if admin_panel.collect_page_errors():
            raise

        print(" [OK]Courier " + courier_id + " status is updated to " + new_courier_status)
    except:
        print(" [FAILED]")
        details = admin_panel.collect_page_errors() or (extra_step_info + [script_step + " error"])
        couriers_not_updated.append((courier_id, details))

driver.close()

if not couriers_not_updated:
    print("All couriers updated correctly.")
else:
    print("Ids of not updated couriers:")
    for failed_item in couriers_not_updated:
        print(failed_item[0])
        print("\n".join(failed_item[1]))
        print()