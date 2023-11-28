import os
import random
import sys
import time
sys.path.append(os.getcwd())  # NOQA

from src.utils.selenium import ChromeDriver

if __name__ == '__main__':

    proxy = {
        'host': '192.40.95.116',
        'port': 12345,
        'username': 'ebay2023',
        'password': 'proxyebaylam'
    }

    driver = ChromeDriver(headless=False, authenticate_proxy=proxy).driver

    driver.set_page_load_timeout(20)
    try:
        driver.get('https://www.newegg.com/lunar-gray-msi-creator-z16p-b12uht-041-content-creation/p/N82E16834156172')
    except Exception as e:
        pass

    with open('test.html', 'w', encoding='utf-8') as f:
        f.write(driver.page_source)

    while True:
        pass
