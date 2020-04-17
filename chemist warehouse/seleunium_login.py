from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
import warnings

warnings.filterwarnings('ignore')
load_dotenv()

url = 'https://www.chemistwarehouse.com.au/'
browser = webdriver.Chrome()
browser.get(url)

browser.find_element(By.ID, "AMS_Login").click()
try:
    element = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, "password1")))
    browser.find_element(By.ID, "password1").send_keys(os.getenv("CWPASSWORD"))
    browser.find_element(By.ID, "username").send_keys(os.getenv("CWUSERNAME"))
    browser.find_element(By.ID, "Signin").click()

    cookies = browser.get_cookies()
    print(cookies)
finally:
    pass
