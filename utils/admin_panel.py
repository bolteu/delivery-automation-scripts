import re
from time import sleep

from selenium.common.exceptions import NoSuchElementException
import math
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from settings.config import base_admin_panel_url, old_base_admin_panel_url

def log(message):
    if False:
        print('@@ ' + message)

def get_element_type(el):
    if el.get_attribute('class') == 'MuiSelect-nativeInput' and el.get_attribute('aria-hidden') == 'true':
        return 'multiselect'
    if el.get_attribute('aria-autocomplete') == 'list':
        return 'autocomplete'
    if el.tag_name == 'select':
        return 'select'
    if el.tag_name == 'textarea':
        return 'text'
    if el.get_attribute('type') == 'checkbox':
        return 'checkbox'
    return 'text'


# Helper class to agregate common admin panel operations
class AdminPanel:
    def __init__(self, driver):
        self.driver = driver

    def collect_page_errors(self):
        log('collect errors')
        return self.driver.execute_script("""
      let errors = [...document.querySelectorAll('.Mui-error.MuiFormHelperText-contained')];
      
      let getErrorText = (el) => {
        try {
          return `${el.previousSibling.querySelector('[name]').getAttribute('name')}: ${el.innerHTML.trim()}`;
        } catch (e) {
          return el.innerHTML.trim();
        }
      }
      return errors.map(getErrorText).filter(Boolean)
    """)

    def wait_for_url_change(self, url_mask, timeout=5):
        log('wait for url change')
        wait = WebDriverWait(self.driver, timeout)
        wait.until(lambda driver: bool(re.search(url_mask, driver.current_url)))

    def login(self, username, password):
        self.driver.get(base_admin_panel_url + "/login?stage=credentials")
        self.driver.implicitly_wait(10)
        self.driver.find_element_by_name("username").send_keys(username)
        self.driver.find_element_by_name("password").send_keys(password)
        self.driver.find_element_by_xpath("//span[contains(text(),'Login')]").click()

    def old_login(self, username, password):
        self.driver.get(old_base_admin_panel_url + "/delivery/Courier/courier/?root_id=1474185")
        self.driver.implicitly_wait(10)
        self.driver.find_element_by_name("username").send_keys(username)
        self.driver.find_element_by_name("password").send_keys(password)
        self.driver.find_element_by_xpath("//div[contains(text(),'Login')]").click()

    def get_form_value(self, field_name):
        log('get form value (' + field_name + ')')
        el = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.NAME, field_name))
        )
        el_type = get_element_type(el)

        if el_type == 'autocomplete':
            return el.get_attribute('value')
        else:
            raise Exception("Get form value is not implemented for " + el_type + " field type")

    def wait_to_be_clickable(self, field_name):
        el = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.NAME, field_name))
        )

    def set_form_value(self, field_name, field_value):
        log('set form value (' + field_name + ', ' + str(field_value) + ')')

        if isinstance(field_value, float) and math.isnan(field_value):
            return
        try:
            el = self.driver.find_element_by_name(field_name)
            el_type = get_element_type(el)
            log('set form value with type (' + field_name + ', ' + str(field_value) + ',' + el_type + ')')

            if el_type == 'multiselect':
                el.find_element_by_xpath("..").click()
                sleep(1)
                select_values = str(field_value).split(',')
                for option in self.driver.find_elements_by_css_selector('.MuiListItem-root'):
                    if option.text.strip() in select_values:
                        option.click()
                        sleep(2)
                self.driver.execute_script(
                    "document.querySelector('[role=\"presentation\"] [aria-hidden=true]') && document.querySelector('[role=\"presentation\"] [aria-hidden=true]').click()")
                sleep(2)

            elif el_type == 'autocomplete':
                self.wait_to_be_clickable(field_name)
                while not el.get_attribute("value") == "":
                  el.send_keys(Keys.BACK_SPACE)

                el.send_keys(str(field_value))

                for option in self.driver.find_elements_by_css_selector('.MuiAutocomplete-option'):
                    if option.text == str(field_value):
                        option.click()
                        break

            elif el_type == 'text':
                el.clear()
                el.send_keys(str(field_value))

            elif el_type == 'checkbox':
                target_value = bool(field_value)
                if field_value == '0':
                    target_value = False
                if el.is_selected() != target_value:
                    el.click()

            elif el_type == 'select':
                for option in el.find_elements_by_tag_name('option'):
                    if option.text == str(field_value):
                        option.click()
                        break
            else:
                print('Unknown element type ', el_type, ' please contact support')
        except NoSuchElementException:
            print('No element with name ', field_name, ' found')

    def save_provider(self, driver):
        driver.implicitly_wait(5)
        save_el = driver.find_element_by_xpath("// span[contains(text(), 'Save')]")
        driver.execute_script("arguments[0].scrollIntoView();", save_el)
        sleep(0.5)
        driver.execute_script("arguments[0].click();", save_el)
        sleep(3)
