import os
import time
import random

import requests
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as ec
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


def logout(driver):
    """Log out of Discord to create another account"""
    print("Logout...")
    driver.execute_script(
        "setInterval(()=>{document.body.appendChild("
        "document.createElement`iframe`).contentWindow.localStorage.token=null},50),setTimeout(()=>{location.reload("
        ")},0);"
    )
    time.sleep(2)
    driver.delete_all_cookies()


def get_email():
    email = input("Please, enter your email: ")

    while True:
        if len(email) > 2:
            if "@gmail.com" and "@" not in email:
                email += "@gmail.com"
            break
        else:
            email = input("Please, enter correct email: ")

    return email


def get_username():
    username = input("Please, enter your username: ")

    while True:
        if len(username) > 2:
            break
        else:
            username = input("Please, enter correct username: ")

    return username


def captcha_solver():
    """Solving hCaptcha with API_KEY and SITE_KEY by 2captcha.com"""
    print("Solving captcha, wait...")
    api_key = os.environ["API_KEY"]
    site_key = "4c672d35-0701-42b2-88c3-78380b0db560"
    url = "https://discord.com/register"
    captcha_request = f"https://2captcha.com/in.php?key={api_key}&method=hcaptcha&sitekey={site_key}&pageurl={url}"

    while True:
        r = requests.get(captcha_request)
        x = r.text
        get_id = x[3:]
        time.sleep(24)
        token_response = (
            f"https://2captcha.com/res.php?key={api_key}&action=get&id={get_id}"
        )
        captcha_answer = requests.get(token_response)
        if captcha_answer.text[3:] == "CHA_NOT_READY":
            print("Captcha is not ready yet, please wait a few seconds")
            continue
        else:
            break
    return captcha_answer.text[3:]


def register_user():
    pwchars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    password = "".join(random.choices(pwchars, k=8))
    email = get_email()
    username = get_username()
    day = int(random.randint(1, 28))
    months = [
        "январь",
        "февраль",
        "март",
        "апрель",
        "май",
        "июнь",
        "июль",
        "август",
        "сентябрь",
        "октябрь",
        "ноябрь",
        "декабрь",
    ]
    month = random.choice(months)
    year = int(random.randint(1980, 2003))

    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://discord.com/register")

    elems = driver.find_elements_by_tag_name("input")
    keys = (email, username, password, day, month + "\ue004", year)

    for text, elem in zip(keys, elems):
        elem.send_keys(text)
        time.sleep(0.05)

    try:
        driver.find_element_by_css_selector('input[type="checkbox"]').click()

        while True:
            driver.find_elements_by_tag_name("button")[0].click()
            try:
                driver.find_element_by_class_name("errorMessage-38vAlK")
                print(
                    "So, you was banned... Ok, lets wait one minute and try it again "
                )
                time.sleep(60)
                continue
            except Exception:
                break

    except Exception as e:
        print(e)

    try:
        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located(
                (By.CSS_SELECTOR, '//iframe[@id="hcaptcha-iframe"]')
            )
        )
    except Exception as e:
        print(e)

    try:

        captcha = captcha_solver()

        driver.execute_script(
            f"document.querySelector('iframe').parentElement.parentElement.__reactProps$.children"
            f".props.onVerify('{captcha}')"
        )

    except Exception as e:
        print(e)

    try:
        WebDriverWait(driver, 20).until(
            lambda driver_url: driver.current_url != "https://discord.com/register"
        )

        token = driver.execute_script(
            'location.reload();var i=document.createElement("iframe");document.body.appendChild(i);return '
            "i.contentWindow.localStorage.token"
        ).strip('"')

        print('{"token": "' + token + '"}')

    except TimeoutException:
        print("Oops, something get wrong...")
        pass

    else:
        print("It's finished, congratulations!!")

    finally:
        logout(driver)

    driver.quit()


if __name__ == "__main__":
    register_user()
