from time import sleep
from selenium import webdriver
import pandas as pd
from utils.admin_panel import AdminPanel, ignore_certificate
from utils.get_cell_value import get_cell_value
from settings.config import username, password, database, chromedriver, base_admin_panel_url
import re
ignore_certificate()

df = pd.read_csv(database)
driver = webdriver.Chrome(chromedriver)
columns = list(df)
admin_panel = AdminPanel(driver=driver)
# ​ Admin-panel login
admin_panel.login(username=username, password=password)
fleets_not_registered = []
for index, row in df.iterrows():
    try:
        driver.implicitly_wait(3)
        driver.execute_script("window.open('" + base_admin_panel_url + "/delivery/fleets/create')")
        driver.switch_to.window(driver.window_handles[index + 1])
        url = driver.current_url
        for column in columns:
            #input(str(column) + ":" + str(get_cell_value(row, column)))
            field_name = column.replace("fleet_", "") #used only for name, since there is a bug using the variable name alone
            admin_panel.set_form_value(field_name, get_cell_value(row, column))
        driver.find_element_by_xpath("//span[contains(text(),'Save')]").click()
        sleep(1)
        driver.implicitly_wait(10)
        driver.implicitly_wait(10)
    except:
        fleets_not_registered.append(get_cell_value(row, "fleet_name"))
if not fleets_not_registered:
    print("All fleets registered correctly.")
else:
    print("Fleet names of not registered fleets:")
    print(fleets_not_registered)