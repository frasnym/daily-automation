from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def CreateChromeWebDrive():
    chrome_options = Options()  # Create ChromeOptions object
    chrome_options.add_argument("--headless")  # Set headless mode
    driver = webdriver.Chrome(
        options=chrome_options
    )  # Create a new instance of the Chrome driver with headless option
    return driver
