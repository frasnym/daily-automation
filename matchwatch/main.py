import json
import os
import sys
import logging
from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

# Add the parent directory to the Python path so you can import from the 'telegram' package.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram.main import send_telegram_message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
LOGIN_URL = "https://www.jamtangan.com/login"
LOGIN_FORM_CLASS = "login-form-container"
POINT_CSS_SELECTOR = r".md\:text-display-m-semibold"


class Result:
    def __init__(self, username: str, point: str):
        self.username = username
        self.point = point


def create_chrome_webdriver() -> webdriver.Chrome:
    """
    Create and return a headless Chrome WebDriver instance.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # type: ignore
    # Additional options can be added as needed.
    return webdriver.Chrome(options=chrome_options)


def get_login_form(
    driver: webdriver.Chrome, wait: WebDriverWait[webdriver.Chrome], url: str
) -> WebElement:
    """
    Navigate to the login page and return the login form element.
    """
    try:
        driver.get(url)
        return wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, LOGIN_FORM_CLASS))
        )
    except Exception as e:
        logger.error(f"Error finding login form: {e}")
        raise


def perform_login(
    driver: webdriver.Chrome,
    username: str,
    password: str,
    wait: WebDriverWait[webdriver.Chrome],
) -> None:
    """
    Perform the login action using the provided credentials.
    """
    try:
        # Find the login form
        login_form = get_login_form(driver, wait, LOGIN_URL)
        if not login_form:
            raise Exception("Login form not found")
        logger.info("Login form found")

        # Enter username
        username_input = login_form.find_element(By.TAG_NAME, "input")  # type: ignore
        if not username_input:
            raise Exception("Username input not found")

        username_input.send_keys(username)  # type: ignore
        logger.info("Username input found and filled")

        # Trigger password input and enter password
        login_form = driver.find_element(By.CLASS_NAME, LOGIN_FORM_CLASS)

        # Assume the second input is for password (index 1)
        password_input = login_form.find_elements(By.TAG_NAME, "input")[1]  # type: ignore
        if not password_input:
            raise Exception("Password input not found")

        password_input.send_keys(password)  # type: ignore
        logger.info("Password input found and filled")

        # Click login button
        login_button = login_form.find_element(By.TAG_NAME, "button")  # type: ignore
        if not login_button:
            raise Exception("Login button not found")

        login_button.click()
        logger.info("Login button clicked")
    except Exception as e:
        logger.error(f"Error performing login: {e}")
        raise


def get_point(wait: WebDriverWait[webdriver.Chrome]) -> str:
    """
    Get user points on dashboard.
    """
    try:
        # Wait for dashboard
        point_el = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, POINT_CSS_SELECTOR))
        )
        logger.info(f"Total points fetched: {point_el.text}")
        return point_el.text
    except Exception as e:
        logger.error(f"Error fetching points: {e}")
        raise


def login_and_get_points(username: str, password: str) -> Result:
    """
    Main function to log in and fetch points and activity history.
    """
    driver = create_chrome_webdriver()
    wait = WebDriverWait(driver, 10)
    logger.info("WebDriver created")

    try:
        perform_login(driver, username, password, wait)
        logger.info("Login successful")

        point = get_point(wait)
        logger.info("Points and last activity fetched")

        return Result(username, point)
    except Exception as e:
        logger.error(f"Error getting points: {e}")
        raise
    finally:
        driver.quit()


def format_message(res: Result) -> str:
    """
    Format the result message.
    """
    message = ""

    if res.username:
        message += f"Username: {res.username}"

    if res.point:
        message += f"\nPoints: {res.point}"

    return message


def main():
    """
    Main script execution.
    """
    title = "⌚ Matchwatch Daily Login"
    hashtag = "matchwatch"
    messages: List[str] = []

    accounts = json.loads(os.environ.get("ACCOUNTS", "[]"))
    for account in accounts:
        try:
            points = login_and_get_points(account["account"], account["password"])
            logger.info(f"Get point of {account['account']} success")
            messages.append(format_message(points))
        except Exception as e:
            messages.append(f"In account {account['account']}; error occurred: {e}")

    final_message = "\n\n".join(messages)
    send_telegram_message(title, final_message, hashtag)


if __name__ == "__main__":
    main()
