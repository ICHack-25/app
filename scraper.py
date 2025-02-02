from typing import List
import time
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def scrape(link: str) -> str:
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(link)

    page_text = driver.find_element(By.TAG_NAME, 'body').text

    driver.quit()

    return page_text


def find(term: str, number_links: str) -> list[str]:
    """
    based on search term, provide top n links from search engine
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)
    driver.get("https://www.google.com")
    search_box = driver.find_element(By.NAME, "q")  # TODO
    search_box.send_keys(term)  # TODO error here
    search_box.send_keys(Keys.RETURN)

    time.sleep(2)

    results = driver.find_elements(By.CSS_SELECTOR, "div.yuRUbf a")

    links = [result.get_attribute("href") for result in results[:number_links]]

    driver.quit()  # Close the browser
    return links