import json
import os
from typing import List
import time

import requests
from dotenv import load_dotenv
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
    load_dotenv()
    API_KEY = os.getenv("SERP_API_KEY")
    link = f"https://serpapi.com/search.json?engine=google&q={term}"

    params = {
        "engine": "google",
        "q": term,
        "api_key": API_KEY,
        "num": number_links
    }

    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()

    links = [result["link"] for result in data["organic_results"]]
    return links