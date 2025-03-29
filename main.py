from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

# import pandas as pd ?? ну пока не нужен

import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from fake_useragent import UserAgent

# Создаём объект для генерации случайных User-Agent’ов
ua = UserAgent()

options = Options()
options.add_argument("--disable-infobars")
options.add_argument(f"--user-agent={ua.random}")  # Устанавливаем случайный User-Agent

browser = webdriver.Firefox(options=options)

try:
    browser.get('https://www.elibrary.ru/authors.asp')
    print(f"Using User-Agent: {browser.execute_script('return navigator.userAgent;')}")  # Проверка User-Agent

    # surname это поле Фамилия, надо ещё добавить SPIN-код
    surname_field = browser.find_element(By.ID, 'surname')

    surname_to_search = input('Введите фамилию : ')
    surname_field.send_keys(surname_to_search)

    code_field = browser.find_element(By.ID, 'codevalue')

    code_to_search = input('Введите SPIN-код : ')
    code_field.send_keys(code_to_search + Keys.RETURN)

    # butred это кнопка Поиск
    share = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'butred'))
    )
    share.click()

    # Даём время загрузиться (можно заменить на WebDriverWait)
    time.sleep(2)

except Exception as e:
    print(f"Ошибка: {e}")

