import os
import sys
sys.path.append(os.getcwd())  # NOQA

from src.utils.selenium import ChromeDriver

if __name__ == '__main__':

    proxy = {
        'host': '23.83.90.228',
        'port': 12345,
        'username': 'ebay2023',
        'password': 'proxyebaylam'
    }

    driver = ChromeDriver(headless=False, authenticate_proxy=proxy).driver

    while True:
        pass
