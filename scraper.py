from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def scrape(link: str) -> str:
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome()
    driver.get(link)

    page_text = driver.find_element(By.TAG_NAME, 'body').text

    driver.quit()

    return page_text


def find(term: str, number_links: str) -> str:
    """
    based on search term, provide top n links from search engine
    """
    # Initialize the WebDriver (e.g., Chrome)
    driver = webdriver.Chrome()

    # Open the webpage
    driver.get("https://example.com")

    # Get the entire text content of the page
    page_text = driver.find_element(By.TAG_NAME, "body").text

    # Print the page text
    print(page_text)

    # Close the WebDriver
    driver.quit()