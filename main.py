from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import UnexpectedAlertPresentException

import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from fake_useragent import UserAgent

### Настройка браузера / user-agent а / установка целевой страницы ### Переменные глобальные!
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

### Функция поиска. Вызов может повторяться, в т.ч., если найдено >1 автора
def search_cycle():
    try:
        # ДОБАВИТЬ ПРОВЕРКУ АВТОРИЗАЦИИ !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # id = win_login, уже не помню где я его там нашел, можешь чекнуть через поиск в инспекции HTML-кода страницы
        # этот id общий для формы вроде, на поля там одинаковый id если я не ошибаюсь, нужно придумать как их заполнить
        # и тыкнуть кнопочку и ура пользователь авторизирован
        # Матвей сделай пж проверку на этот id
        # я сделал в main (изначально бесконечный) цикл, чтобы при ошибке, можно было заново начать поиск, чтобы не запускать скрипт заново
        # не знаю оставим этот подход или нет, но пока
        # нужно сделать проверку есть ли элемент с этим id на сайте :
        ## если есть - пользователь не авторизован, напиши заполнение этой формы (чтобы данные вводить в консоль) и авторизацию
        ## если нет - пользователь авторизован, все хорошо, продолжаем выполнение цикла
        # upd. лучше напиши авторизацию отдельной функцией

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