from smtpd import Options

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

options = Options()
options.headless = True

driver = webdriver.Chrome(options=options)
driver.get("https://www.politifact.com/")

text_elements = driver.find_elements(By.XPATH, "//body//*[not(self::script or self::style)]")
text = [element.text for element in text_elements]

image_elements = driver.find_elements(By.TAG_NAME, "img")
images = [img.get_attribute("src") for img in image_elements]

# Output the text and images
print("Text:", text)
print("Images:", images)

# Close the browser
driver.quit()
