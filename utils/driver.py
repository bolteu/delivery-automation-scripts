from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import  Chrome


driver = Chrome(service =  Service(ChromeDriverManager().install()))