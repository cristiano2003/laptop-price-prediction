import os
import sys
sys.path.append(os.getcwd())  # NOQA

from src.utils.selenium import ChromeDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup as bs

if __name__ == '__main__':
    driver = ChromeDriver(headless=False, disable_images=True).driver

    # url = 'https://www.newegg.com/classic-black-msi-modern-14-c7m-049us-work-business/p/N82E16834156445'
    # url = 'https://www.newegg.com/black-hasee-z8-gaming/p/2WC-004U-00037?Item=9SIBDT0JEC8108&cm_sp=SP-_-1826825-_-Pers_CategorySponsoredProduct-_-4-_-9SIBDT0JEC8108-_-223-_--_-6'
    # url = 'https://www.newegg.com/classic-black-msi-modern-14-c11m-068us-work-business/p/N82E16834156464?Item=N82E16834156464'
    # url = 'https://www.newegg.com/acer-cb314-3h-c4vs/p/N82E16834360290?Item=N82E16834360290'
    # url = 'https://www.newegg.com/space-gray-apple-macbook-pro-fkgq3ll-a-home-personal/p/N82E16834096420'
    # url = 'https://www.newegg.com/black-lenovo-thinkpad-x1-extreme-20mf000lus-gaming-entertainment/p/N82E16834847265?Item=9SIADG3HWD2054'
    url = 'https://www.newegg.com/black-lenovo-thinkpad-l14-gen-2-work-business/p/1TS-000E-172K3?Item=9SIADG3JU37572'

    driver.get(url)

    # WebDriverWait(driver, 30).until(
    #     EC.presence_of_all_elements_located((By.CLASS_NAME, 'table-horizontal'))
    # )

    soup = bs(driver.page_source, 'html.parser')

    with open('test.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
