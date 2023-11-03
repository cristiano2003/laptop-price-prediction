import os 
import sys 
sys.path.append(os.getcwd()) # NOQA

from src.utils.selenium import ChromeDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup as bs

if __name__ == '__main__':
    driver = ChromeDriver(headless=False, disable_images=True).driver
    
    url = 'https://www.newegg.com/classic-black-msi-modern-14-c7m-049us-work-business/p/N82E16834156445'
    
    driver.get(url)
    
    # WebDriverWait(driver, 30).until(
    #     EC.presence_of_all_elements_located((By.CLASS_NAME, 'table-horizontal'))
    # )
    
    soup = bs(driver.page_source, 'html.parser')
    
    with open('test.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())