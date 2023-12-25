import os
import sys
sys.path.append(os.getcwd())  # NOQA

import json
import time
import traceback
import requests

from bs4 import BeautifulSoup as bs

from src.crawler.base import BaseCrawler
from concurrent.futures import ThreadPoolExecutor, as_completed


class Anphat(BaseCrawler):

    MAX_PAGES = 10

    def __init__(self):
        self.anphat_config = self.load_config('anphat.json')

        # Connect to the database
        self.conn = self.connect_db('introds.db')

    ############################ Parse the product category page ############################

    def __parse_category_page(self, url: str) -> dict:
        """
            Get all the product links from a category page
        Args:
            url (str): The url of a category page

        Returns:
            dict: The status, message and data of the request
        """

        urls = []

        try:
            response = requests.get(url)

            # If text "Sản phẩm đang được cập nhật" exist in the page
            if 'Sản phẩm đang được cập nhật' in response.text:
                return {
                    'status': 'error',
                    'message': f'Error: {url} is not available',
                    'data': []
                }

            soup = bs(response.text, 'html.parser')

            # List container
            container = soup.find('div', {'class': 'p-list-container d-flex flex-wrap'})
            list_divs = container.find_all('div', {'class': 'p-item js-p-item'})

            for product in list_divs:
                href = product.find('a').get('href')
                product_url = f'https://www.anphatpc.com.vn{href}'
                urls.append(product_url)

            return {
                'status': 'success',
                'message': f'Get product urls of {url} successfully',
                'data': urls
            }
        except Exception as e:
            self.log(f"Error: {str(e)}")

            return {
                'status': 'error',
                'message': f'Error: {str(e)}',
                'data': []
            }

    def _get_product_urls(self, manufacturer: str) -> list:
        """
            Go through all the pages and get the product urls of each manufacturer
        Args:
            manufacturer (str): hp, dell, asus, acer, lenovo, msi, lg
        """

        urls = []

        url = self.anphat_config[manufacturer]
        self.log(f"==>> {manufacturer.upper()} url: {url}")

        # Get all the pages of the manufacturer
        url_list_pages = [f'{url}?page={i}' for i in range(1, self.MAX_PAGES + 1)]

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self.__parse_category_page, url) for url in url_list_pages]

            # Get the results
            for future in as_completed(futures):
                result = future.result()
                if result['status'] == 'success':
                    self.log(f'==> {result["message"]}: {len(result["data"])} products', color='green')
                    urls.extend(result['data'])
                else:
                    self.log(f'==> {result["message"]}', color='red')

        self.log('==>> Total products: {}'.format(len(urls)))

        return urls

    def get_all_product_links(self):
        """
            Get all the product urls of all the manufacturers
        """

        save_dir = 'data/anphat'
        os.makedirs(save_dir, exist_ok=True)

        anphat_product_links = {}

        for manufacturer in self.anphat_config:
            self.log(f'========>> Getting product urls of {manufacturer.upper()}', color='yellow')
            urls = self._get_product_urls(manufacturer)
            anphat_product_links[manufacturer] = urls

        # Save the product links to a json file
        with open(os.path.join(save_dir, 'anphat_product_links.json'), 'w') as f:
            json.dump(anphat_product_links, f, indent=4, ensure_ascii=False)

        self.log('========>> Done!', color='green')

    ############################ Fetch all the htmls ############################

    def __fetch_html(self, url: str) -> dict:
        """
            Fetch the html of a product page
        Args:
            url (str): The url of a product page

        Returns:
            dict: The status, message and data of the request
        """

        try:
            response = requests.get(url)

            if response.status_code == 200:
                return {
                    'status': 'success',
                    'message': f'Get {url} successfully',
                    'data': response.text
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Error: {url} is not available',
                    'data': []
                }

        except Exception as e:
            self.log(f"Error: {str(e)}")

            return {
                'status': 'error',
                'message': f'Error: {str(e)}',
                'data': []
            }

    def crawl_raw_htmls(self):

        # Load the anphat product links
        with open('data/anphat/anphat_product_links.json', 'r') as f:
            anphat_product_links = json.load(f)

        # Create the directory to save the htmls
        save_dir = 'data/anphat/raw_htmls'
        os.makedirs(save_dir, exist_ok=True)

        # Go through all the manufacturers
        for manufacturer in anphat_product_links:
            self.log(f'========>> Getting raw htmls of {manufacturer.upper()}', color='yellow')

            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = {}

                # Go through all the product urls
                for url in anphat_product_links[manufacturer]:
                    futures[executor.submit(self.__fetch_html, url)] = url

                # Get the results
                for idx, future in enumerate(as_completed(list(futures.keys()))):
                    url = futures[future]
                    result = future.result()

                    if result['status'] == 'success':
                        self.log(f'==>{idx:>3}|{len(list(futures.keys())):<3} {result["message"]}', color='green')

                        # Save the html
                        save_path = f'data/anphat/raw_htmls/{manufacturer}_{idx}.html'
                        with open(save_path, 'w', encoding='utf-8') as f:
                            f.write(result['data'])

                        # Insert to the database
                        self.conn.execute(f"""
                            INSERT INTO anphat_fetch_results (Manufacturer, Url, Raw_html_path)
                            VALUES 
                            ('{manufacturer}', '{url}', '{save_path}')
                                          """)
                        self.conn.commit()

                    else:
                        self.log(f'==>{idx:>3}|{len(list(futures.keys())):<3} {result["message"]}', color='red')

    ############################ Parse the raw htmls ############################

    def __extract_raw_features(self, html_path: str) -> dict:
        """
            Extract the raw features from the raw html
        Args:
            html_path (str): The path to the raw html

        Returns:
            dict: The raw features
        """

        # Get the information in the database
        result = self.conn.execute(f"""
            select Manufacturer, Url, Raw_html_path from anphat_fetch_results
            where Raw_html_path = '{html_path}'
                          """).fetchone()

        manufacturer = result[0]
        url = result[1]
        raw_html_path = result[2]

    def parse_specs(self):
        raw_htmls_dir = 'data/anphat/raw_htmls'

        raw_htmls_path = [os.path.join(raw_htmls_dir, x) for x in os.listdir(raw_htmls_dir) if x.endswith('.html')]


if __name__ == "__main__":
    anphat = Anphat()
    # anphat.get_all_product()
    anphat.crawl_raw_htmls()

    anphat.conn.close()
