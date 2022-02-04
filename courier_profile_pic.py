from settings.config import py_drive_secret
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import json
import os
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from utils.admin_panel import AdminPanel, get_element_type
from utils.get_cell_value import get_cell_value
from settings.config import username, password, database, chromedriver, base_admin_panel_url
from selenium.webdriver.common.keys import Keys
import re
# Save json to a temporary file dict

a_file = open('client_secrets.json', 'w')
json.dump(py_drive_secret, a_file)
a_file.close()
gauth = GoogleAuth()
gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.
# Create GoogleDrive instance with authenticated GoogleAuth instance.
drive = GoogleDrive(gauth)


driver = webdriver.Chrome(chromedriver)
driver.maximize_window()
admin_panel = AdminPanel(driver=driver)
admin_panel.login(username=username, password=password)

df = pd.read_csv(database)
columns = list(df)
total_lines = len(list(df.iterrows()))

partners_with_issue = []
script_step = ''
extra_step_info = []

for index, row in df.iterrows():
    extra_step_info = []
    print(row)
    partner_id = row.partner_id
    print("{index} / {total_lines} - {partner_id}".format(index=index + 1, total_lines=total_lines, partner_id=partner_id, end=""))
    try:
        script_step = 'add pic to partner profile'
        driver.implicitly_wait(20)
        # partner profile:
        driver.get(base_admin_panel_url + "/fleet-root/partners/edit/" + str(partner_id))
        # download picture
        for column in columns:
            if column == 'partner_id': continue
            if column == 'profile_pic_url':
                file_id = re.findall('file\/d\/([^\/]+)\/', get_cell_value(row, column))[0]
                print(file_id)
                pfile = drive.CreateFile({'id': file_id})
                pfile.GetContentFile(f"{partner_id}.png")
                print(os.path.basename(f"{partner_id}.png"))
                el = driver.find_element(By.CSS_SELECTOR, "input[type = 'file']")
                print(os.path.basename(f"2352788.png"))
                el.send_keys(os.path.abspath(f"2352788.png"))
                driver.find_element(By.XPATH, "//span[contains(text(),'Upload image')]").find_element(By.XPATH,'..').click()
                driver.find_element(By.XPATH, "//span[contains(text(),'Save')]").click()
    except:
        print("[FAILED]")
        details = admin_panel.collect_page_errors() or (extra_step_info + [script_step + " error"])
        partners_with_issue.append((partner_id, details))

for item in ['client_secrets.json', f"{partner_id}.png"]:
    os.remove(item)