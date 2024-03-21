import json
import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def CreateChromeWebDrive():
    chrome_options = Options()  # Create ChromeOptions object
    options = [
        "--headless",
        # "--disable-gpu",
        # "--window-size=1920,1200",
        # "--ignore-certificate-errors",
        # "--disable-extensions",
        # "--no-sandbox",
        # "--disable-dev-shm-usage",
    ]
    for option in options:
        chrome_options.add_argument(option)
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def GetPoint(username: str, password: str) -> dict:
    result = {
        "username": username,
        "point": None,
        "last": None,
        "process": [],
        "err": None,
    }

    driver = CreateChromeWebDrive()  # init driver

    driver.get("https://www.jamtangan.com/login")  # Open the website
    wait = WebDriverWait(driver, 10)  # Wait timeout, Adjust the timeout as needed

    login_form = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "login-form-container"))
    )  # Wait until the form class is found
    if login_form is None:
        result["err"] = "form is not found"
        return result
    result["process"].append("form found: {}".format(login_form.get_attribute("class")))

    # Find username input
    username_input = login_form.find_element(By.TAG_NAME, "input")
    if username_input is None:
        result["err"] = "username_input is not found"
        return result
    result["process"].append(
        "username_input found: {}".format(username_input.get_attribute("class"))
    )
    username_input.send_keys(username)  # Type username

    # Trigger password to show up
    # Find form again. Why? because password input show after username is typed
    login_form = driver.find_element(By.CLASS_NAME, "login-form-container")
    result["process"].append(
        "login_form 2 found: {}".format(login_form.get_attribute("class"))
    )

    # Find password input
    form_inputs = login_form.find_elements(By.TAG_NAME, "input")
    if len(form_inputs) <= 1:
        result["err"] = "form_inputs len is LTE 1"
        return result
    form_inputs[1].send_keys(password)  # Type username

    button_el = login_form.find_element(
        By.TAG_NAME, "button"
    )  # Find submit login button
    if button_el is None:
        result["err"] = "button_el is not found"
        return result
    result["process"].append("button_el found: {}".format(button_el.text))

    button_el.click()  # clicking the button

    # Wait dashboard
    total_el = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".text-primary-1.body-text-3"))
    )
    result["process"].append(f"total_el 1 found: {total_el.text}")

    # Get Today Point
    driver.get("https://www.jamtangan.com/account/membership/activities")
    time.sleep(2)

    # Total point
    total_el = driver.find_element(
        By.CSS_SELECTOR, ".text-primary-1 .text-sm+ .text-sm"
    )
    result["point"] = total_el.text
    result["process"].append(f"total_el 2 found: {total_el.text}")

    # Loop through the history
    history_els = driver.find_elements(By.CLASS_NAME, "point-item")
    for el in history_els:
        result["last"] = el.text
        result["process"].append(f"last point history found: {el.text}")
        break

    driver.quit()

    return result


# Send the message using the Telegram bot API
def send_telegram_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {"chat_id": chat_id, "text": text}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Error sending message. Status code: {response.status_code}")


def ForwardToTelegram(BOT_TOKEN: str, CHAT_ID: str, result: dict):
    messages: list[str] = []
    messages.append("from: py-matchwatch-loggin #matchwatch\n")
    messages.append("username: {}".format(result["username"]))
    if result["err"] is not None:
        messages.append("err: {}".format(result["err"]))
        messages.append("process: {}".format(result["process"]))
    else:
        messages.append("point: {}".format(result["point"]))
        messages.append("last: {}".format(result["last"]))

    separator = "\n"  # Customize the separator as needed
    finalMessage = separator.join(str(x) for x in messages)

    send_telegram_message(BOT_TOKEN, CHAT_ID, finalMessage)


def main():
    accounts = json.loads(os.environ.get("ACCOUNTS"))
    for acc in accounts:
        res = GetPoint(acc["account"], acc["password"])
        print(json.dumps(res))
        ForwardToTelegram(os.environ.get("BOT_TOKEN"), os.environ.get("CHAT_ID"), res)


# Call the main function if this script is executed
if __name__ == "__main__":
    main()
