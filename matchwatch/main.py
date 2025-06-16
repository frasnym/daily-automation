import json
import os
import sys
import time
from typing import List, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC


# Add the parent directory to the Python path so you can import from the 'telegram' package.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram.main import send_telegram_message


class Result:
    def __init__(self, username: str, point: str, last: str):
        self.username = username
        self.point = point
        self.last = last


def create_chrome_webdriver() -> webdriver.Chrome:
    """
    Create and return a headless Chrome WebDriver instance.
    """
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # Additional options can be added as needed.
    return webdriver.Chrome(options=chrome_options)


def get_login_form(
    driver: webdriver.Chrome, wait: WebDriverWait[webdriver.Chrome], url: str
) -> WebElement:
    """
    Navigate to the login page and return the login form element.
    """

    driver.get(url)
    return wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "login-form-container"))
    )


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
        login_form = get_login_form(driver, wait, "https://www.jamtangan.com/login")

        if not login_form:
            raise Exception("Login form not found")

        print(f"Login form found: {login_form.get_attribute('class')}")  # type: ignore

        # Enter username
        username_input = login_form.find_element(By.TAG_NAME, "input")  # type: ignore
        if not username_input:
            raise Exception("Username input not found")

        username_input.send_keys(username)  # type: ignore
        print(
            f"Username input found and filled: {username_input.get_attribute('class')}"  # type: ignore
        )

        # Trigger password input and enter password
        login_form = driver.find_element(By.CLASS_NAME, "login-form-container")
        password_input = login_form.find_elements(By.TAG_NAME, "input")[  # type: ignore
            1
        ]  # Assume the second input is for password
        if not password_input:
            raise Exception("Password input not found")

        password_input.send_keys(password)  # type: ignore
        print("Password input found and filled")

        # Click login button
        login_button = login_form.find_element(By.TAG_NAME, "button")  # type: ignore
        if not login_button:
            raise Exception("Login button not found")

        login_button.click()
        print("Login button clicked")

        # Wait for dashboard
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".text-primary-1.body-text-3")
            )
        )
        print("Dashboard loaded")
    except Exception as e:
        print("Error performing login")
        print(e)
        raise Exception("Error logging in")


def fetch_points(driver: webdriver.Chrome) -> Tuple[str, str]:
    """
    Fetch user points and activity history.
    """

    try:
        driver.get("https://www.jamtangan.com/account/membership/activities")
        time.sleep(2)  # Temporary wait; ideally replaced with WebDriverWait

        # Fetch total points
        total_el = driver.find_element(
            By.CSS_SELECTOR, ".text-primary-1 .text-sm+ .text-sm"
        )
        point = total_el.text
        print(f"Total points fetched: {total_el.text}")

        # Fetch last activity
        history_els = driver.find_elements(By.CLASS_NAME, "point-item")
        last = ""
        if history_els:
            last = history_els[0].text
            print(f"Last activity fetched: {history_els[0].text}")

        return point, last

    except Exception as e:
        print("Error fetching points")
        print(e)
        raise Exception("Error fetching points")


def get_points(username: str, password: str) -> Result:
    """
    Main function to log in and fetch points and activity history.
    """

    driver = create_chrome_webdriver()
    wait = WebDriverWait(driver, 10)
    print("WebDriver created")

    try:
        perform_login(driver, username, password, wait)
        print("Login successful")

        point, last = fetch_points(driver)
        print("Points and last activity fetched")

        return Result(username, point, last)
    except Exception as e:
        print("Error fetching points")
        print(e)
        raise Exception("Error fetching points")
    finally:
        driver.quit()


def format_message(res: Result) -> str:
    return f"Username: {res.username}\nPoints: {res.point}\nLast activity: {res.last}"


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
            points = get_points(account["account"], account["password"])
            print(f"get point of {account['account']} success\n")

            messages.append(format_message(points))
        except Exception as e:
            messages.append(f"in account {account['account']}; error occurred: {e}")

    final_message = "\n\n".join(messages)
    send_telegram_message(title, final_message, hashtag)


if __name__ == "__main__":
    main()
