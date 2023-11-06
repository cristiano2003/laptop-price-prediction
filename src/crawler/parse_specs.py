import json
import os
import re
import time
import sys
sys.path.append(os.getcwd())  # NOQA

from src.utils.selenium import ChromeDriver
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup as bs
from dev_tools_supporter import sout
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.utils.proxy import check_proxy

from src.utils.database.mongodb import MongoDB


class LaptopSpecParse():

    raw_htmls_dir = os.path.join(os.getcwd(), 'src', 'crawler', 'raw_htmls')
    proxy_path = os.path.join(os.getcwd(), 'assets', 'proxies.txt')
    current_html_idx = 0

    def __init__(self, urls: list) -> None:
        self.urls = urls
        self.db = MongoDB(cluster='newegg')

    def __process_text(self, text: str, battery: bool = False):
        # Strip
        text = text.strip()

        unexpected_chars = ['\n', '\t', '\r', '\"']

        unexpected_chars += '.' if not battery else []

        for c in unexpected_chars:
            text = text.replace(c, '')

        # Remove long spaces
        list_text = text.split(' ')
        # Remove empty string
        list_text = list(filter(lambda x: x != '', list_text))
        # Join
        text = ' '.join(list_text)

        return text

    def parse_html(self, url: str, html: str) -> dict:
        try:
            # -------------------------------------------- Init -------------------------------------------- #
            data = {}
            soup = bs(html, 'html.parser')
            data['url'] = url

            # -------------------------------------------- Parse the price -------------------------------------------- #
            div_price = soup.find('div', {'class': 'product-price'})
            ul_price = div_price.find('ul', {'class': 'price'})
            current_price = ul_price.find('li', {'class': 'price-current'})
            strong = current_price.find('strong')
            sup = current_price.find('sup')

            data['price'] = float(
                f'{self.__process_text(strong.text.replace(",", ""))}.{self.__process_text(sup.text)}')

            # -------------------------------------------- Parse the specs -------------------------------------------- #

            # Find all the tables with class: table-horizontal
            tables = soup.find_all('table', {'class': 'table-horizontal'})
            found_refresh_rate = False  # If the refresh rate is not found, set it to 60 Hz

            for table in tables:
                tbody = table.find('tbody')
                rows = tbody.find_all('tr')

                for row in rows:
                    th = row.find('th')
                    cells = row.find_all('td')

                    property_name = self.__process_text(th.text).lower()

                    # Properties must have:
                    if property_name == 'brand':
                        data['brand'] = self.__process_text(cells[0].text)

                    elif property_name in ('cpu cpu', 'cpu'):
                        data['cpu'] = self.__process_text(cells[0].text)

                    elif property_name in ('screen size screen size', 'screen size'):
                        data['screen_size'] = self.__process_text(cells[0].text)

                    elif property_name in ('resolution resolution', 'resolution'):
                        data['screen_resolution'] = self.__process_text(cells[0].text)

                    elif property_name in ('memory memory', 'memory'):
                        data['memory'] = self.__process_text(cells[0].text)

                    elif property_name in ('ssd ssd', 'ssd'):
                        ssd_storage = self.__process_text(cells[0].text)
                        if ssd_storage != 'No':
                            data['storage'] = ssd_storage

                    elif property_name in ('hdd hdd', 'hdd'):
                        if data.get('storage') is not None:
                            continue

                        hdd_storage = self.__process_text(cells[0].text)
                        if hdd_storage != 'No':
                            data['storage'] = hdd_storage

                    elif property_name in ('graphic type graphic type', 'graphic type'):
                        data['graphic_type'] = self.__process_text(cells[0].text)

                    elif property_name in ('gpu/vpu gpu/vpu', 'gpu/vpu'):
                        data['graphic_name'] = self.__process_text(cells[0].text)

                    elif property_name in ('weight weight', 'weight'):
                        data['weight'] = self.__process_text(cells[0].text)

                    elif property_name in ('ac adapter ac adapter', 'ac adapter', 'battery battery', 'battery'):
                        battery = self.__process_text(cells[0].text)

                        regex = [r'(\d+) wh', r'(\d+)wh', r'(\d+)-watt', r'(\d+) whrs',
                                 r'(\d+)whrs', r'(\d+)whr', r'(\d+) whr']

                        for r in regex:
                            match = re.search(r, battery.lower())
                            if match:
                                data['battery'] = match.group(1) + ' whrs'

                                break
                    else:
                        # Properties may have:
                        if property_name == 'refresh rate':
                            found_refresh_rate = True
                            data['refresh_rate'] = self.__process_text(cells[0].text)

            if not found_refresh_rate:
                data['refresh_rate'] = '60 Hz'

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Exception when parsing html: {e}',
                'data': None
            }
        else:
            return {
                'status': 'success',
                'message': 'Parsing html successfully',
                'data': data
            }

    def fetch_url(self, url: str, proxy: tuple = None, proxy_idx: int = None) -> dict:
        """
            This method used to fetch the html of each page from detail pages, there are 
            about 3000 products in total. Using proxies is required to avoid CAPTCHA.
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

        # -----------------------------------------------Parse the html to get information-----------------------------------------------

        html_name = f'raw_{LaptopSpecParse.current_html_idx}.html'
        LaptopSpecParse.current_html_idx += 1

        with open(os.path.join(self.raw_htmls_dir, html_name), 'w', encoding='utf-8') as f:  # Save the raw html
            f.write(driver.page_source)

        response = self.parse_html(url, driver.page_source)

        if response['status'] == 'error':
            return response
        else:
            spec = response['data']

        return {
            'status': 'success',
            'message': f'Fetching url "{url}" successfully',
            'data': spec
        }

    def run(self, max_worker: int = 5):
        specs: list = []

        # ---------------------------------------------Reading Proxies---------------------------------------------
        sout('Reading proxies ...', 'yellow')

        with open(self.proxy_path, 'r') as f:
            proxies: list = list(map(lambda x: x.strip(), f.readlines()))

        proxies = list(map(lambda x: x.split(':'), proxies))

        current_proxy_idx: int = 0  # Proxy index (To ensure that we will use all proxy instead of random)

        # -----------------------------------------------Crawl Urls-----------------------------------------------
        with ThreadPoolExecutor(max_workers=max_worker) as executor:
            futures = {}

            sout('Submitting urls to executor ...', 'yellow')

            for idx, url in enumerate(self.urls):

                # Check whether the current proxy is working or not
                while True:
                    if current_proxy_idx == len(proxies):
                        current_proxy_idx = 0

                    if check_proxy(proxies[current_proxy_idx]):
                        break
                    else:
                        sout(f'Proxy {proxies[current_proxy_idx]} is not working. Skipping ...', 'red')
                        current_proxy_idx += 1

                sout(f'Using proxy {proxies[current_proxy_idx]} to fetch url "{url}"', 'green')

                if current_proxy_idx == len(proxies):
                    current_proxy_idx = 0  # Reset the index of current proxy

                future = executor.submit(self.fetch_url, url=url,
                                         proxy=proxies[current_proxy_idx], proxy_idx=current_proxy_idx)
                current_proxy_idx += 1

                futures[future] = url

            sout('Waiting for the results ...', 'yellow')
            for idx, future in enumerate(as_completed(list(futures.keys()))):
                result = future.result()

                if result['status'] == 'success':
                    sout(f'Get detail urls from "{futures[future]}" successfully', 'green')

                    number_of_features = len(result['data'])

                    sout(f'Number of features: {number_of_features}', 'green')

                    if number_of_features >= 9:
                        # Set value of not existed properties to None
                        properties = ['brand', 'cpu', 'screen_size', 'screen_resolution', 'memory', 'storage',
                                      'graphic_type', 'graphic_name', 'weight', 'battery', 'refresh_rate']

                        for prop in properties:
                            if result['data'].get(prop) is None:
                                result['data'][prop] = None

                        specs.append(result['data'])
                        self.db.update_collection('laptops', result['data'])
                        sout('Updated to database successfully', 'green')

                else:
                    sout(str(result), 'red')

            sout('Done', 'green')

            print(specs)


if __name__ == '__main__':
    # Get the urls from the output_urls.json
    urls = []

    for i in range(1, 4):
        with open(os.path.join(os.getcwd(), 'src', 'crawler', 'data', 'detail_urls', f'output_urls_{i}.json'), 'r') as f:
            urls.extend(json.loads(f.read()))

    # Divide the urls into pars, each part has 200 urls
    urls = [urls[i:i + 200] for i in range(0, len(urls), 200)]

    for url in urls:
        parser = LaptopSpecParse(urls=url)
        parser.run(max_worker=10)

        # Sleep 10 minutes
        sout('Sleeping 4 minutes ...', 'red')

        for i in range(60 * 4):
            print(f'Time remaining: {60 * 4 - i} seconds\r', end='')
            time.sleep(1)
