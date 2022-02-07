# This Python file uses the following encoding: utf-8
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from utils.admin_panel import AdminPanel, get_element_type, get_unique
from utils.get_cell_value import get_cell_value
from settings.config import username, password, database, chromedriver, base_admin_panel_url
from selenium.webdriver.common.keys import Keys
import re

df = pd.read_csv(database)
driver = webdriver.Chrome(chromedriver)
driver.maximize_window()
columns = list(df)

admin_panel = AdminPanel(driver=driver)
admin_panel.login(username=username, password=password)

couriers_not_updated = []
script_step = ''
extra_step_info = []

for courier_id in get_unique(df['courier_id']):

        script_step = 'read_comments_file'
        comments = df[df['courier_id'] == courier_id]['text']
        driver.implicitly_wait(20)
        driver.get(base_admin_panel_url + "/delivery-courier/couriers/" + str(courier_id))  # get courier profile
        script_step = 'add_courier_comments'
        try:
            for c in comments:
                comms_box = driver.find_element(By.XPATH, "//p[contains(text(),'Comments')]").find_element(By.XPATH, "..")
                comms_box.find_element(By.CSS_SELECTOR, "a[role = 'button']").click() #open comment field
                admin_panel.set_form_value('text', c)
                driver.find_element(By.XPATH, "//span[contains(text(),'Add comment')]").find_element(By.XPATH, "..").click()
            print(f"[OK]Courier {courier_id} comments added.")
            sleep(0.5)
        except:
            print("FAILED")
            details = admin_panel.collect_page_errors() or (extra_step_info + [script_step + " error"])
            couriers_not_updated.append((courier_id, c, details))

driver.close()

if not couriers_not_updated:
    print("All couriers have been updated correctly.")
else:
    print("Ids of not updated couriers:")
    for failed_item in couriers_not_updated:
        print(failed_item[0])
        print("\n".join(failed_item[1]))
        print()