import json
import requests
import os
import sys
sys.path.append(os.getcwd())  # NOQA

from concurrent.futures import ThreadPoolExecutor, as_completed
from dev_tools_supporter import printProgressBar, sout
from bs4 import BeautifulSoup as bs

from src.utils.selenium import ChromeDriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


urls = [f'https://www.newegg.com/Laptops-Notebooks/SubCategory/ID-32/Page-{i}' for i in range(1, 11)]
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


def parse_url(page_source: str) -> list:
    output_hrefs: list = []

    soup = bs(page_source, 'html.parser')

    body = soup.find(
        'div', {'class': 'item-cells-wrap border-cells short-video-box items-grid-view four-cells expulsion-one-cell'})

    items = body.find_all('div', {'class': 'item-container'})

    for item in items:
        a_tag = item.find('a')
        href = a_tag.get('href', None)
        if href:
            output_hrefs.append(href)

    return output_hrefs


def fetch_url(url: str, proxy: tuple = None, proxy_idx: int = None) -> dict:
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

    driver = ChromeDriver(headless=False, authenticate_proxy=proxy_config,
                          disable_images=True, proxy_index=proxy_idx).driver

    while number_of_tried <= 5:
        try:
            number_of_tried += 1
            driver.set_page_load_timeout(20)

            sout(f'Fetching the url "{url}" {number_of_tried} time(s)')
            driver.get(url)
            break
        except TimeoutException:
            break
        except Exception:
            sout(f'Exception when fetching url: "{url}". Retrying ...', 'red')
            continue

    if number_of_tried > 5:
        return {
            'status': 'error',
            'message': f'Fetching url "{url}" unsuccessfully',
            'data': {
                'error_url': url
            }
        }

    # -----------------------------------------------Parse the html to get urls-----------------------------------------------
    urls: list = parse_url(driver.page_source)

    return {
        'status': 'success',
        'message': f'Fetching url "{url}" successfully',
        'data': urls
    }


def run(max_worker: int = 5):
    output_urls: list = []

    # ---------------------------------------------Reading Proxies---------------------------------------------
    sout('Reading proxies ...', 'yellow')

    with open(proxy_path, 'r') as f:
        proxies: list = list(map(lambda x: x.strip(), f.readlines()))

    proxies = list(map(lambda x: x.split(':'), proxies))

    current_proxy_idx: int = 0  # Proxy index (To ensure that we will use all proxy instead of random)

    # -----------------------------------------------Crawl Urls-----------------------------------------------
    with ThreadPoolExecutor(max_workers=max_worker) as executor:
        futures = {}

        sout('Submitting urls to executor ...', 'yellow')
        for idx, url in enumerate(urls):
            if current_proxy_idx == len(proxies):
                current_proxy_idx = 0  # Reset the index of current proxy

            future = executor.submit(fetch_url, url=url, proxy=proxies[current_proxy_idx], proxy_idx=current_proxy_idx)
            current_proxy_idx += 1

            futures[future] = url

        sout('Waiting for the results ...', 'yellow')
        for idx, future in enumerate(as_completed(list(futures.keys()))):
            result = future.result()

            if result['status'] == 'success':
                sout(f'Get detail urls from "{futures[future]}" successfully', 'green')
                sout(f'Number of urls: {len(result["data"])}', 'green')
                output_urls.extend(result['data'])

        sout('Done', 'green')

        # TODO: Store the output_urls in src/crawler/data as output_urls.json

        data_folder = os.path.join(os.getcwd(), 'src', 'crawler', 'data')

        os.makedirs(data_folder, exist_ok=True)

        with open(os.path.join(data_folder, 'output_urls.json'), 'w') as f:
            f.write(json.dumps(output_urls, indent=4))


if __name__ == '__main__':
    run(max_worker=5)
