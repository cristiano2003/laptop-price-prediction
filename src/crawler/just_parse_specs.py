"""
    In this file, we will parse the specs agains from the html files. 
    
    Work flow:
    
    -   Parse the price of the product
    
    -   Parse the brand (AMD, MSI, ASUS, etc).
    
    -   Parse the cpu (i7-9700k, i9-9900k, etc)
    
    -   Parse the screen size (15.6", 17.3", etc)
    
    -   Parse the screen resolution (1920x1080, 3840x2160, etc)
    
    -   Parse the refresh rate (144Hz, 240Hz, etc).
    
    -   Parse the ram (16GB, 32GB, etc)
    
    -   Parse the storage (512GB SSD, 1TB SSD, etc). If both SSD and HDD are available, we just get the SSD.
    
    -   Parse the graphic_type (Dedicated Card, Integrated Card, etc)
    
    -   Parse the graphic_name (RTX 2060, RTX 2070, etc)
    
    -   Parse the weight (4.5 lbs, 5.5 lbs, etc)
    
    -   Parse the battery capacity (56.6Wh, 99.9Wh, etc)
    
    Note: 
    
    Try to look for brand, cpu, screen size, screen resolution, refresh rate, ram, storage from the title of the product.
"""

import os
import sys
sys.path.append(os.getcwd())  # NOQA

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dev_tools_supporter import sout
from bs4 import BeautifulSoup as bs

from src.utils.openai import chat_completion

HTML_DIR = os.path.join(os.getcwd(), 'src/crawler/raw_htmls')


class LaptopSpecParse():

    def __init__(self, file_name: str):
        self.file_name = file_name
        self.specs = {}

        with open(os.path.join(HTML_DIR, self.file_name), 'r', encoding='utf-8') as f:
            page_source = f.read()

        self.soup = bs(page_source, 'html.parser')

    def _process_text(self, text: str, remove_dot: bool = False) -> str:
        """
            This method used to process the text
        Args:
            text (str): The text to be processed
            remove_dot (bool, optional): Defaults to False.

        Returns:
            str : The processed text
        """
        # Remove leading and trailing spaces
        text = text.strip()

        # Remove unexpected characters
        unexpected_chars = ['\n', '\t', '\r', '\"']
        for c in unexpected_chars:
            text = text.replace(c, '')

        # Remove dot for getting the price
        if remove_dot:
            text = text.replace('.', '')

        # Remove long spaces
        list_text = text.split(' ')

        # Remove empty string
        list_text = list(filter(lambda x: x != '', list_text))

        # Join
        text = ' '.join(list_text)

        return text

    def _parse_from_title(self) -> dict:
        """
            Parse the specs from the title of the product

            Output:
            ```python
                {
                    'status'  :  'success' or 'error'
                    'message' :  'str'
                    'data'    :   None | {
                        'brand'             :  'str' | None
                        'cpu_manufacture'   :  'str' | None
                        'cpu_name'          :  'str' | None
                        'cpu_generation'    :  'str' | None
                        'cpu_clock_speed'   :  'str' | None
                        'screen_size'       :  'str' | None
                        'screen_resolution' :  'str' | None
                        'refresh_rate'      :  'str' | None
                        'ram'               :  'str' | None
                        'storage'           :  'str' | None
                    }
                }
            ```
        """

        # Get the title
        try:
            self.title = self.soup.find('h1', {'class': 'product-title'}).text.strip()
        except Exception as e:
            message = f'Parse title of "{self.file_name}" unsuccessfully: {str(e)}'

            sout(message)
            return {
                'status': 'error',
                'message': message,
                'data': None
            }

        # TODO: Parse the above specs from the title using ChatGPT API Prompts using "chat_completion" function: Nam Nguyen

    def _parse_html(self) -> dict:
        try:
            # -------------------------------------------- Init -------------------------------------------- #
            data = {}

            # -------------------------------------------- Parse the price -------------------------------------------- #
            div_price = self.soup.find('div', {'class': 'product-price'})
            ul_price = div_price.find('ul', {'class': 'price'})
            current_price = ul_price.find('li', {'class': 'price-current'})
            strong = current_price.find('strong')
            sup = current_price.find('sup')

            data['price'] = float(
                f'{self._process_text(strong.text.replace(",", ""), remove_dot=True)}.{self._process_text(sup.text, remove_dot=True)}')

            # -------------------------------------------- Parse the specs -------------------------------------------- #

            # Find all the tables with class: table-horizontal
            tables = self.soup.find_all('table', {'class': 'table-horizontal'})
            found_refresh_rate = False  # If the refresh rate is not found, set it to 60 Hz

            for table in tables:
                tbody = table.find('tbody')
                rows = tbody.find_all('tr')

                for row in rows:
                    th = row.find('th')
                    cells = row.find_all('td')

                    property_name = self._process_text(th.text).lower()

                    # Properties must have:
                    if property_name == 'brand':
                        data['brand'] = self._process_text(cells[0].text)

                    elif property_name in ('cpu cpu', 'cpu'):
                        data['cpu'] = self._process_text(cells[0].text)

                    elif property_name in ('screen size screen size', 'screen size'):
                        data['screen_size'] = self._process_text(cells[0].text)

                    elif property_name in ('resolution resolution', 'resolution'):
                        data['screen_resolution'] = self._process_text(cells[0].text)

                    elif property_name in ('memory memory', 'memory'):
                        data['memory'] = self._process_text(cells[0].text)

                    elif property_name in ('ssd ssd', 'ssd'):
                        ssd_storage = self._process_text(cells[0].text)
                        if ssd_storage != 'No':
                            data['storage'] = ssd_storage

                    elif property_name in ('hdd hdd', 'hdd'):
                        if data.get('storage') is not None:
                            continue

                        hdd_storage = self._process_text(cells[0].text)
                        if hdd_storage != 'No':
                            data['storage'] = hdd_storage

                    elif property_name in ('graphic type graphic type', 'graphic type'):
                        data['graphic_type'] = self._process_text(cells[0].text)

                    elif property_name in ('gpu/vpu gpu/vpu', 'gpu/vpu'):
                        data['graphic_name'] = self._process_text(cells[0].text)

                    elif property_name in ('weight weight', 'weight'):
                        data['weight'] = self._process_text(cells[0].text)

                    elif property_name in ('ac adapter ac adapter', 'ac adapter', 'battery battery', 'battery'):
                        battery = self._process_text(cells[0].text)

                        regex = [r'(\d+(\.\d+)?) wh', r'(\d+(\.\d+)?)wh', r'(\d+(\.\d+)?)-watt', r'(\d+(\.\d+)?) whrs',
                                 r'(\d+(\.\d+)?)whrs', r'(\d+(\.\d+)?)whr', r'(\d+(\.\d+)?) whr']

                        for r in regex:
                            match = re.search(r, battery.lower())
                            if match:
                                data['battery'] = match.group(1) + ' whrs'

                                break
                    else:
                        # Properties may have:
                        if property_name == 'refresh rate':
                            found_refresh_rate = True
                            data['refresh_rate'] = self._process_text(cells[0].text)

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

    def result(self) -> dict:
        """
            Combine the result of parsing the html and title of the product
        Returns:
            dict: 
            ```python
            {
                'brand'             :  'str' | None
                'cpu_manufacture'   :  'str' | None
                'cpu_name'          :  'str' | None
                'cpu_generation'    :  'str' | None
                'cpu_clock_speed'   :  'str' | None 
                'screen_size'       :  'str' | None
                'screen_resolution' :  'str' | None
                'refresh_rate'      :  'str' | None
                'ram'               :  'str' | None
                'storage'           :  'str' | None
                'graphic_type'      :  'str' | None
                'graphic_name'      :  'str' | None
                'weight'            :  'str' | None
                'battery'           :  'str' | None
            }
            ```
        """

        # TODO: Parse the specs from the title of the product: Nguyen Hoang


if __name__ == '__main__':

    htmls: list = os.listdir(HTML_DIR)

    for html in htmls:
        pass

    # TODO: Export the dictionary to a csv file: Truc Nguyen
