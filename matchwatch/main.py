import json
import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def create_chrome_webdriver():
    """
    Create and return a headless Chrome WebDriver instance.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    # Additional options can be added as needed.
    return webdriver.Chrome(options=chrome_options)


def get_login_form(driver, wait, url):
    """
    Navigate to the login page and return the login form element.
    """
    driver.get(url)
    return wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "login-form-container"))
    )


def perform_login(driver, username, password, wait):
    """
    Perform the login action using the provided credentials.
    """
    result = {"process": [], "err": None}

    login_form = get_login_form(driver, wait, "https://www.jamtangan.com/login")
    if not login_form:
        result["err"] = "Login form not found"
        print("[ERR] Login form not found")
        return result

    result["process"].append(f"Login form found: {login_form.get_attribute('class')}")
    print("Login form found")

    # Enter username
    username_input = login_form.find_element(By.TAG_NAME, "input")
    if not username_input:
        result["err"] = "Username input not found"
        print("[ERR] Username input not found")
        return result

    username_input.send_keys(username)
    result["process"].append(
        f"Username input found and filled: {username_input.get_attribute('class')}"
    )
    print("Username input found and filled")

    # Trigger password input and enter password
    login_form = driver.find_element(By.CLASS_NAME, "login-form-container")
    password_input = login_form.find_elements(By.TAG_NAME, "input")[
        1
    ]  # Assume the second input is for password
    if not password_input:
        result["err"] = "Password input not found"
        print("[ERR] Password input not found")
        return result

    password_input.send_keys(password)
    result["process"].append("Password input found and filled")
    print("Password input found and filled")

    # Click login button
    login_button = login_form.find_element(By.TAG_NAME, "button")
    if not login_button:
        result["err"] = "Login button not found"
        print("[ERR] Login button not found")
        return result

    login_button.click()
    result["process"].append("Login button clicked")
    print("Login button clicked")

    # Wait for dashboard
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".text-primary-1.body-text-3"))
    )
    result["process"].append("Dashboard loaded")
    print("Dashboard loaded")

    return result


def fetch_points(driver, wait, result):
    """
    Fetch user points and activity history.
    """
    driver.get("https://www.jamtangan.com/account/membership/activities")
    time.sleep(2)  # Temporary wait; ideally replaced with WebDriverWait

    # Fetch total points
    total_el = driver.find_element(
        By.CSS_SELECTOR, ".text-primary-1 .text-sm+ .text-sm"
    )
    result["point"] = total_el.text
    result["process"].append(f"Total points fetched: {total_el.text}")
    print("Total points fetched")

    # Fetch last activity
    history_els = driver.find_elements(By.CLASS_NAME, "point-item")
    if history_els:
        result["last"] = history_els[0].text
        result["process"].append(f"Last activity fetched: {history_els[0].text}")
        print("Last activity fetched")

    return result


def get_points(username: str, password: str) -> dict:
    """
    Main function to log in and fetch points and activity history.
    """
    result = {
        "username": username,
        "point": None,
        "last": None,
        "process": [],
        "err": None,
    }

    driver = create_chrome_webdriver()
    wait = WebDriverWait(driver, 10)

    try:
        login_result = perform_login(driver, username, password, wait)
        result["process"].extend(login_result["process"])
        if login_result["err"]:
            result["err"] = login_result["err"]
            return result

        fetch_points(driver, wait, result)
    except Exception as e:
        result["err"] = str(e)
    finally:
        driver.quit()

    return result


def send_telegram_message(token, chat_id, text):
    """
    Send a message via Telegram bot API.
    """
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {"chat_id": chat_id, "text": text}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Error sending message. Status code: {response.status_code}")


def forward_to_telegram(bot_token: str, chat_id: str, results: list[dict]):
    """
    Format and send aggregated results to Telegram in a single message.
    """
    messages = [f"source: {os.environ.get('APP')} #matchwatch"]

    for result in results:
        messages.append(f"\nUsername: {result['username']}")
        if result["err"]:
            messages.append(f"Error: {result['err']}")
            messages.append(f"Process: {result['process']}")
        else:
            messages.append(f"Points: {result['point']}")
            messages.append(f"Last activity: {result['last']}")

    final_message = "\n".join(messages)
    send_telegram_message(bot_token, chat_id, final_message)


def main():
    """
    Main script execution.
    """
    accounts = json.loads(os.environ.get("ACCOUNTS", "[]"))
    results = []

    for account in accounts:
        result = get_points(account["account"], account["password"])
        results.append(result)
        print(json.dumps(result, indent=4))  # Keep this for debugging or logs

    # Send a single Telegram message for all accounts
    forward_to_telegram(os.environ.get("BOT_TOKEN"), os.environ.get("CHAT_ID"), results)


if __name__ == "__main__":
    main()
