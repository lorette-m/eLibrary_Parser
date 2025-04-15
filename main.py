from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import UnexpectedAlertPresentException, NoSuchElementException, TimeoutException

import time
import traceback
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from fake_useragent import UserAgent

### Настройка браузера / user-agent и установка целевой страницы ###
# Создаём объект для генерации случайных User-Agent’ов
ua = UserAgent()
options = Options()
options.add_argument("--disable-infobars")
options.add_argument(f"--user-agent={ua.random}")  # Устанавливаем случайный User-Agent

browser = webdriver.Firefox(options=options)

browser.get('https://www.elibrary.ru/authors.asp')
print(f"Using User-Agent: {browser.execute_script('return navigator.userAgent;')}")  # Проверка User-Agent

class AuthorizationException(Exception):
    pass

def authorize():
    try:
    # Функция авторизации кароче если на странице обнаружен элемент с id 'win_login', значит
    # gользователь не авторизован беда вообще запрашивает ввод данных, заполняет форму авторизации
    # и потом кликает на кнопку входа
        
        # ЕСЛИ КАПЧА ТО БЕДА БЕДОВАЯ
        login_container = browser.find_element(By.ID, 'win_login')
        print("Пользователь не авторизован. Переходим к авторизации.")
        
        login_field = login_container.find_element(By.ID, 'login')
        password_field = login_container.find_element(By.ID, 'password')
        
        user_login = input('Введите логин или почту: ')
        user_password = input('Введите пароль: ')
        
        login_field.clear()
        login_field.send_keys(user_login)
        password_field.clear()
        password_field.send_keys(user_password)

        login_button = login_container.find_element(By.CLASS_NAME, 'butred')
        login_button.click()
        
        time.sleep(2)
        browser.get('https://www.elibrary.ru/authors.asp')
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'surname')))
        print("Авторизация выполнена.")
    except Exception as e:
        print("Ошибка при авторизации:")
        traceback.print_exc()
        raise AuthorizationException("Не удалось авторизоваться. Проверьте введенные данные.")

def search_cycle():
    try:
        try:
            browser.find_element(By.ID, 'win_login')
            authorize()
        except NoSuchElementException:
            print("Пользователь уже авторизован.")
        
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

        WebDriverWait(browser, 5).until(EC.alert_is_present())

        alert = browser.switch_to.alert
        if alert:
            print("Alert text:", alert.text)
            alert.dismiss()
            print("Alert dismissed... Throwing an exception")
            raise AuthorizationException("Ошибка авторизации. Для парсинга необходимо авторизироваться в eLibrary")

        # authors_table = browser.find_element(By.ID, 'restab')
        # rows_in_table = authors_table.find_element(By.TAG_NAME, 'tr')
        # if len(rows_in_table) > 4:
        #    print('Найдено более одного автора по данному запросу. Уточните полное ФИО или код автора')

        # Даём время загрузиться (можно заменить на WebDriverWait)
        time.sleep(2)
    except Exception as e:
        print(f"Ошибка: {e}")

def main():
    loop_limit = 3
    loop_iteration = 0
    while loop_iteration < loop_limit:
        try:
            if search_cycle(): # При успешном выполнении выйдет из цикла
                break
        except Exception as e:
            print(f"Произошла ошибка: {e}")
        loop_iteration += 1

if __name__ == "__main__":
    main()