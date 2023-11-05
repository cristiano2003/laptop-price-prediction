import requests
import os
import sys
sys.path.append(os.getcwd())  # NOQA

from concurrent.futures import ThreadPoolExecutor, as_completed

from src.utils.selenium import ChromeDriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


urls = [f'https://www.newegg.com/Laptops-Notebooks/SubCategory/ID-32/Page-{i}' for i in range(1, 101)]
proxy_path = os.path.join(os.getcwd(), 'assets', 'proxies.txt')

headers = {
    'authority': 'www.newegg.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'vi,en-US;q=0.9,en;q=0.8,vi-VN;q=0.7',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}


def fetch_url(url: str, proxy: tuple = None) -> dict:
    """
        This method used to fetch the html of each page from newegg product catagories, there are 
        100 pages in total. Using proxies is required to avoid CAPTCHA.
    Args:
        url (str): The url of each catagories
        proxy (tuple): The rotate proxy for each url (host, port, username, password)

    Returns:
        dict: The result of fetching process
        ```python
            {
                'status'  :  'success' or 'error'
                'message' :  'str'
                'data'    :  'str' (html) | None
            }
        ```
    """

    host, port, username, password = proxy

    proxy_config = {
        'host': host,
        'port': int(port),
        'username': username,
        'password': password
    }

    number_of_tried = 0

    driver = ChromeDriver(headless=False, authenticate_proxy=proxy_config, disable_images=True).driver

    while number_of_tried <= 5:
        try:
            number_of_tried += 1
            driver.set_page_load_timeout(5)

            print(f'Fetching the url "{url}" {number_of_tried + 1} time(s)')
            driver.get(url)
            break
        except TimeoutException:
            break
        except Exception as e:
            print(f'Exception when fetching url: "{url}". Retrying ...')
            continue

    if number_of_tried > 5:
        return {
            'status': 'error',
            'message': f'Fetching url "{url}" unsuccessfully',
            'data': {
                'error_url': url
            }
        }

    return {
        'status': 'success',
        'message': f'Fetching url "{url}" successfully',
        'data': driver.page_source
    }


def parse_url(page_source: str):
    pass


def run():
    pass


if __name__ == '__main__':
    # Read the proxies
    with open(proxy_path, 'r') as f:
        proxies: list = list(map(lambda x: x.strip(), f.readlines()))

    proxies = list(map(lambda x: x.split(':'), proxies))

    print(proxies[0])

    result = fetch_url(
        url='https://www.newegg.com/Laptops-Notebooks/SubCategory/ID-32/Page-2',
        proxy=proxies[1]
    )

    with open('test.html', 'w', encoding='utf-8') as f:
        f.write(result['data'])
