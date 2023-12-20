import os
import random
import sys
import time
sys.path.append(os.getcwd())  # NOQA

from src.utils.selenium import ChromeDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

if __name__ == '__main__':

    proxy = {
        'host': '45.147.244.54',
        'port': 61288,
        'username': 's87ZDs1N',
        'password': 'xBRd2S9m'
    }

    driver = ChromeDriver(headless=False, authenticate_proxy=proxy).driver

    driver.set_page_load_timeout(20)
    try:
        driver.get('https://www.newegg.com/lunar-gray-msi-creator-z16p-b12uht-041-content-creation/p/N82E16834156172')
    except Exception as e:
        pass

    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="table-comparison"]'))
    )

    with open('test.html', 'w', encoding='utf-8') as f:
        f.write(driver.page_source)

    while True:
        pass
