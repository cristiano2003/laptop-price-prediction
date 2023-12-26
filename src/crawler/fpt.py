import os
import sys
sys.path.append(os.getcwd())  # NOQA

import json
import time
import traceback

from src.utils.selenium import ChromeDriver


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs

from src.crawler.base import BaseCrawler
from concurrent.futures import ThreadPoolExecutor, as_completed


class Fpt(BaseCrawler):

    # Load the category mapping config
    def __init__(self, headless: bool = False):
        self.fpt_config = self.load_config('fpt.json')
        self.headless = headless

        # Connect to the database
        self.conn = self.connect_db('introds.db')

    # ----------------- Get all product links -----------------

    def __parse_product_links(self, page_source: str) -> list:
        urls = []

        try:
            soup = bs(page_source, 'html.parser')
            box = soup.find('div', {'class': 'card fplistbox'})
            items = box.find_all('div', {'class': 'cdt-product prd-lap'})

            for item in items:
                href = item.find('a').get('href')
                url = f'https://fptshop.com.vn{href}'
                urls.append(url)

        except Exception as e:
            self.log(traceback.format_exc())
        finally:
            self.log(f'Found {len(urls)} product links')
            return urls

    def __get_product_link(self, driver, manufacturer: str) -> list:
        """
            Get all product links of a manufacturer in The Gioi Di Dong
        Args:
            manufacturer (str): hp, dell, asus, lenovo, acer, msi

        Returns:
            list: The list of all product links of that manufacturer in The Gioi Di Dong
        """

        # Go the the manufacturer page
        self.log(f'Going to the manufacturer page: {self.fpt_config[manufacturer]}')
        driver.get(self.fpt_config[manufacturer])

        # Parsing the page source
        self.log('Parsing the page source')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.card.fplistbox')))
        urls = self.__parse_product_links(driver.page_source)

        return urls

    def get_all_product_links(self):
        """
            Get all product links of all manufacturers in The Gioi Di Dong
        """
        # Get the driver
        self.log('Getting the driver')
        driver = ChromeDriver(headless=self.headless).driver

        urls = {}

        for manufacturer in self.fpt_config.keys():
            urls[manufacturer] = self.__get_product_link(driver=driver, manufacturer=manufacturer)

        # Close the driver
        self.log('Closing the driver')
        driver.close()

        # Save the result to file
        os.makedirs('data/fpt', exist_ok=True)
        self.log('Saving the result to file')
        with open('data/fpt/fpt_product_links.json', 'w') as f:
            json.dump(urls, f, indent=4, ensure_ascii=False)

    # ----------------- Fetch all raw_htmls -----------------

    def crawl_raw_htmls(self):
        """
            Crawl the raw HTML of all product pages
        Args:
            url (str): The product page URL

        Returns:
            str: The raw HTML of the product page
        """

        def fetch_html(url, manufacturer: str, id: int) -> bool:
            try:
                driver = ChromeDriver(headless=self.headless).driver
                driver.get(url)
                html = driver.page_source

                time.sleep(1)

                os.makedirs('data/fpt/raw_htmls', exist_ok=True)
                with open(f'data/fpt/raw_htmls/{manufacturer}_{id}.html', 'w', encoding='utf-8') as f:
                    f.write(html)

                print('========> Successfully fetch HTML of', url)

                time.sleep(3)

                driver.execute_script("""
                show_more_btn = document.getElementsByClassName('re-link js--open-modal')
                show_more_btn[0].click()""")

                time.sleep(1.5)

                data = driver.execute_script("""
                details = document.getElementsByClassName('card card-normal')
                detail = details[0].innerHTML
                return detail;""")

                if data:
                    print('========> Successfully fetch detail HTML of', url)

                os.makedirs('data/fpt/detail_htmls', exist_ok=True)
                with open(f'data/fpt/detail_htmls/{manufacturer}_{id}.html', 'w', encoding='utf-8') as f:
                    f.write(data)

                craw_info = {
                    'Manufacturer': manufacturer,
                    'Url': url,
                    'Raw_html_path': f'data/fpt/raw_htmls/{manufacturer}_{id}.html',
                    'Detail_specs_html_path': f'data/fpt/detail_htmls/{manufacturer}_{id}.html'
                }

                self.log(f'========> Successfully fetch HTML of {url}')

                return craw_info
            except Exception as e:
                self.log(f'========> Fail to fetch HTML of {url}: {str(e)}')
                return False

        def build_insert_query(manufacturer: str, url: str, raw_html_path: str, detail_html_path: str) -> str:
            return f"""
                INSERT INTO fpt_fetch_results (Manufacturer, Url, Raw_html_path, Detail_specs_html_path)
                VALUES ('{manufacturer}', '{url}', '{raw_html_path}', '{detail_html_path}')
            """

        # Read the product links
        self.log(f'Start fetching ...')

        with open('data/fpt/fpt_product_links.json', 'r') as f:
            fpt_product_links: dict = json.load(f)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []

            for manufacturer in fpt_product_links.keys():
                for id, url in enumerate(fpt_product_links[manufacturer]):
                    futures.append(executor.submit(fetch_html, url, manufacturer, id))

            for future in as_completed(futures):
                if not future.result():
                    continue

                # If success, then insert to database
                result = future.result()
                manufacturer = result['Manufacturer']
                url = result['Url']
                raw_html_path = result['Raw_html_path']
                detail_html_path = result['Detail_specs_html_path']
                self.conn.execute(build_insert_query(manufacturer, url, raw_html_path, detail_html_path))
                self.conn.commit()

        self.log(f'Finish fetching ...')

    # ----------------- Parse raw_htmls -----------------
    def parse_specs(self, html_path: str):
        with open(html_path, 'r', encoding='utf-8') as f:
            soup = bs(f.read(), 'html.parser')

        # Get the product name
        product_name = soup.find('h1').text.strip()

        # Get the box price
        box_price = soup.find('div', {'class': 'box-price'})

        # A function to process the price
        def process_price(price: str) -> int:
            try:
                price = price.replace('₫', '')
                price = price.replace('*', '')
                while '.' in price:
                    price = price.replace('.', '')

                price = price.strip()
                return int(price)
            except:
                return price

        # Get the price
        try:
            present_price: int = process_price(box_price.find('p', {'class': 'box-price-present'}).text.strip())
        except:
            present_price = None  # Do not have present price
        try:
            old_price: str = box_price.find('p', {'class': 'box-price-old'}).text.strip()
            old_price: int = process_price(old_price)
        except:
            old_price = None  # Do not have old price

        if old_price:
            discount = round((old_price - present_price) / old_price, 2)
        else:
            discount = None

        # Buid the raw specs
        def build_raw_specs() -> str:
            raw_specs = ''

            parameter = soup.find('div', {'class': 'parameter'})
            ul = parameter.find('ul')
            lis = ul.find_all('li')

            for li in lis:
                feature = li.find('p', {'class': 'lileft'}).text.strip()
                info = li.find('div', {'class': 'liright'}).text.strip()

                info_list = list(map(lambda x: x.strip(), info.split('\n')))
                info = ', '.join(info_list)

                raw_specs += f'{feature}: {info}\n'

            return raw_specs

        raw_specs = build_raw_specs()

        return {
            'html_path': html_path,
            'product_name': product_name,
            'present_price': present_price,
            'old_price': old_price,
            'discount': discount,
            'raw_specs': raw_specs
        }


if __name__ == '__main__':
    fpt = Fpt(headless=True)
    # fpt.get_all_product_links()
    fpt.crawl_raw_htmls()
