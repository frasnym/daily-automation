from matchwatch.driver import CreateChromeWebDrive

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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
    # Total point. Wait until the element with class "text-primary-1" and "body-text-3" is found
    total_el = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".text-primary-1.body-text-3"))
    )
    result["point"] = total_el.text
    result["process"].append(f"total_el found: {total_el.text}")

    # Get Today Point
    driver.get("https://www.jamtangan.com/account/membership/activities")

    # Loop through the history
    history_els = driver.find_elements(By.CLASS_NAME, "point-item")
    for el in history_els:
        result["last"] = el.text
        result["process"].append(f"last point history found: {el.text}")
        break

    driver.quit()

    return result
