import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from fake_useragent import UserAgent

import getpass

import csv
from bs4 import BeautifulSoup

### Настройка браузера / user-agent и установка целевой страницы ###
# Создаём объект для генерации случайных User-Agent’ов
ua = UserAgent()
options = Options()
options.add_argument("--disable-infobars")
options.add_argument(f"--user-agent={ua.random}")  # Устанавливаем случайный User-Agent

browser = webdriver.Firefox(options=options)

# Размер и позиция для правой половины экрана (у меня 1920x1200, масштаб 125%)
browser.set_window_size(768, 918)
browser.set_window_position(768, 0)

browser.get('https://www.elibrary.ru/authors.asp')
print(f"Using User-Agent: {browser.execute_script('return navigator.userAgent;')}")  # Проверка User-Agent

class AuthorizationException(Exception):
    """Исключение, возникающее при проблемах с авторизацией."""
    def __init__(self, message="Не удалось авторизоваться. Проверьте введенные данные."):
        self.message = message
        super().__init__(self.message)
class AuthorTableMoreOneRow(Exception):
    """Исключение, возникающее, если найдено слишком много авторов."""
    def __init__(self, message="Найдено более одного автора по данному запросу. Уточните полное ФИО или код автора"):
        self.message = message
        super().__init__(self.message)

def authorize():
    """
    Функция авторизации, вызывается если пользователь не авторизован (на странице обнаружен элемент с id 'win_login'). \n
    Запрашивает ввод данных, заполняет форму авторизациии, кликает на кнопку входа.
    """
    try:
        login_container = browser.find_element(By.ID, 'win_login')
        print("Пользователь не авторизован. Переходим к авторизации...")
        
        login_field = login_container.find_element(By.ID, 'login')
        password_field = login_container.find_element(By.ID, 'password')

        # Можно указать учетные данные для автозаполнения
        user_login = ""
        user_password = ""

        #user_login = input('Введите логин или почту: ')
        #user_password = input('Введите пароль: ')

        login_field.clear()
        login_field.send_keys(user_login)
        password_field.clear()
        password_field.send_keys(user_password)

        # Чекбокс "Запомнить меня"
        checkbox = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.NAME, 'knowme'))
        )
        if not checkbox.is_selected():
            checkbox.click()
            print("Чекбокс \"Запомнить меня\" отмечен.")
        else:
            print("Чекбокс \"Запомнить меня\" уже установлен.")

        login_button = login_container.find_element(By.CLASS_NAME, 'butred')
        login_button.click()

        WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.ID, 'surname')))
        print("Авторизация выполнена.")
    except (TimeoutException, NoSuchElementException) as e:
        raise AuthorizationException("Не удалось авторизоваться. Проверьте элементы формы.") from e

def search_cycle():
    """
    Основная функция работы с сайтом, выполняющая поиск, сохранение статистики и нужной веб-страницы.
     1. Проверка на авторизацию.
     2. Поиск по Фамилии и SPIN-коду.
     3. Проверка таблицы результатов поиска (должен быть один автор).
     4. Сбор количества статей со страницы статистики автора.
     5. Переход на страницу статей, выбор категорий, поиск, сохранение веб-страницы.
    NB: В графу "Фамилия" можно указать полное ФИО, допустимо пропустить SPIN-код, но тогда может быть несколько авторов с одинаковым ФИО.
    """
    try:
        ### Проверки на случай повторных итераций в цикле main

        # Проверяем, находимся ли на начальной странице, если нет — переходим
        if browser.current_url != 'https://www.elibrary.ru/authors.asp':
            browser.get('https://www.elibrary.ru/authors.asp')
            print("Перешли на начальную страницу.")

        # Закрываем все лишние вкладки, оставляем только основную
        if len(browser.window_handles) > 1:
            for window_handle in browser.window_handles[1:]:
                browser.switch_to.window(window_handle)
                browser.close()
            browser.switch_to.window(browser.window_handles[0])
            print("Закрыты лишние вкладки.")

        try:
            browser.find_element(By.ID, 'win_login')
            authorize()
        except NoSuchElementException:
            print("Пользователь уже авторизован.")

        surname_field = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, 'surname'))
        )
        surname_field.clear()
        code_field = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, 'codevalue'))
        )
        code_field.clear()

        # Тестовые данные: Лукин 7065-3430
        surname_to_search = "Лукин"
        code_to_search = "7065-3430"

        #surname_to_search = input('Введите фамилию : ')
        #code_to_search = input('Введите SPIN-код : ')

        surname_field.send_keys(surname_to_search)
        code_field.send_keys(code_to_search + Keys.RETURN)

        share = WebDriverWait(browser, 10).until(
           EC.element_to_be_clickable((By.CLASS_NAME, 'butred'))
        )
        share.click()

        try:
            WebDriverWait(browser, 5).until(EC.alert_is_present())
            alert = browser.switch_to.alert
            print("Alert text:", alert.text)
            alert.dismiss()
            raise AuthorizationException("Ошибка авторизации. Для парсинга необходимо авторизироваться в eLibrary")
        except TimeoutException:
            print("Alert не появился, продолжаем выполнение...")

        ### Работа с таблицей

        authors_table = WebDriverWait(browser, 15).until(
            EC.presence_of_element_located((By.ID, 'restab'))
        )
        rows_in_table = authors_table.find_elements(By.TAG_NAME, 'tr')
        print(f"Найдено строк в таблице: {len(rows_in_table)}")
        if len(rows_in_table) > 4:
            raise AuthorTableMoreOneRow()

        ### Собираем количество статей на странице со статистикой

        statistical_page = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((
            By.XPATH,
            '//a[contains(@href, "author_profile.asp?id=") and contains(@title, "Анализ публикационной активности")]'
            ))
        )
        statistical_page.click()
        print("Страница статистики загружена.")

        # Количество всех публикаций
        publications_total_elib = WebDriverWait(browser, 15).until(
            EC.presence_of_element_located((
                By.XPATH,
                '//a[contains(@href, "author_items.asp") and contains(@title, "Полный список публикаций")]'
            ))
        ).text

        # Публикаций в РИНЦ
        publications_rinc = WebDriverWait(browser, 15).until(
            EC.presence_of_element_located((
                By.XPATH,
                '//a[contains(@href, "author_items.asp") and contains(@title, "Список публикаций автора в РИНЦ")]'
            ))
        ).text

        # Публикаций в ядре РИНЦ
        publications_rinc_core = WebDriverWait(browser, 15).until(
            EC.presence_of_element_located((
                By.XPATH,
                '//a[contains(@href, "author_items.asp") and contains(@title, "Список публикаций автора, входящих в ядро РИНЦ")]'
            ))
        ).text

        browser.back()

        ### Переходим на страницу с публикациями в РИНЦ

        print("Переходим на страницу с публикациями в РИНЦ...")

        rinc_link = WebDriverWait(browser, 15).until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//a[contains(@href, "author_items.asp") and contains(@title, "Список публикаций данного автора в РИНЦ")]'
            ))
        )

        original_window = browser.current_window_handle

        rinc_link.click()

        WebDriverWait(browser, 15).until(EC.number_of_windows_to_be(2))

        for window_handle in browser.window_handles:
            if window_handle != original_window:
                browser.switch_to.window(window_handle)

        print("Перешли на страницу списка публикаций в РИНЦ.")

        types_header = WebDriverWait(browser, 15).until(
            EC.element_to_be_clickable((By.ID, 'hdr_types'))
        )
        types_header.click()

        checkbox_articles = WebDriverWait(browser, 15).until(
            EC.element_to_be_clickable((By.ID, 'types_RAR'))
        )
        checkbox_articles.click()

        cats_header = WebDriverWait(browser, 15).until(
            EC.element_to_be_clickable((By.ID, 'hdr_cats'))
        )
        cats_header.click()

        categories = [
            {"id": "cats_risc", "name": "Публикации, включенные в РИНЦ"},
            {"id": "cats_corerisc", "name": "Публикации, включенные в ядро РИНЦ"},
            {"id": "cats_whitelist1", "name": "Статьи в журналах, включенных в Белый список (уровень 1)"},
            {"id": "cats_whitelist2", "name": "Статьи в журналах, включенных в Белый список (уровень 2)"},
            {"id": "cats_whitelist3", "name": "Статьи в журналах, включенных в Белый список (уровень 3)"},
            {"id": "cats_whitelist4", "name": "Статьи в журналах, включенных в Белый список (уровень 4)"},
            {"id": "cats_rsci", "name": "Статьи в журналах, входящих в RSCI"},
            {"id": "cats_scopus1", "name": "Статьи в журналах, входящих в Scopus (квартиль 1)"},
            {"id": "cats_scopus2", "name": "Статьи в журналах, входящих в Scopus (квартиль 2)"},
            {"id": "cats_scopus3", "name": "Статьи в журналах, входящих в Scopus (квартиль 3)"},
            {"id": "cats_scopus4", "name": "Статьи в журналах, входящих в Scopus (квартиль 4)"}
        ]

        # Сайт может сохранять состояние чекбоксов, нужно пройтись и проверить, что галочек нет
        for category in categories:
            checkbox = WebDriverWait(browser, 5).until(
                EC.element_to_be_clickable((By.ID, category["id"]))
            )
            if checkbox.is_selected():
                checkbox.click()

        print("Выберите категории публикаций (введите номера через пробел, например: 1 3 5):")
        for i, category in enumerate(categories, 1):
            print(f"{i}. {category['name']}")

        # Получаем выбор пользователя
        selected_indices = input("Ваш выбор: ").split(" ")
        selected_indices = [int(i.strip()) - 1 for i in selected_indices if i.strip().isdigit()]

        # Проверяем валидность ввода
        if not selected_indices or max(selected_indices) >= len(categories) or min(selected_indices) < 0:
            print("Неверный выбор категорий.")
            return

        # Кликаем на выбранные чекбоксы
        for index in selected_indices:
            checkbox_id = categories[index]["id"]
            checkbox = WebDriverWait(browser, 15).until(
                EC.element_to_be_clickable((By.ID, checkbox_id))
            )
            if not checkbox.is_selected():  # Проверяем, не стоит ли галочка
                checkbox.click()

        container = WebDriverWait(browser, 15).until(
            EC.presence_of_element_located((By.ID, 'show_param'))
        )
        search_button = container.find_element(
            By.XPATH,
            './/div[contains(@class, "butred") and contains(@onclick, "pub_search()")]'
        )

        old_table = browser.find_element(By.ID, 'restab')

        browser.execute_script("arguments[0].click();", search_button)

        WebDriverWait(browser, 15).until(EC.staleness_of(old_table))
        WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.ID, 'restab')))

        with open("page.html", "w", encoding="utf-8") as f:
            f.write(browser.page_source)
        print("Страница сохранена в page.html")

        return publications_total_elib, publications_rinc, publications_rinc_core
    except AuthorizationException:
        raise
    except AuthorTableMoreOneRow:
        raise
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        browser.get('https://www.elibrary.ru/authors.asp')
        print("Перешли на начальную страницу из-за ошибки.")
        raise

class Article:
    def __init__(self, number, name):
        self.number = number
        self.name = name
    def write_down(self):
        line = self.number + " " + self.name
        return line

def parse_elibrary_html(html_path, csv_path, publications_total_elib, publications_rinc, publications_rinc_core):
    with open(html_path, encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    lines = soup.find('table', id='restab').find_all('b')
    articles = []
    current_number = 0
    for line in lines:
        if(current_number < 3):
            current_number += 1
            continue
        elif(current_number % 2 != 0):
            number = line.text.replace('\n', ' ').strip()
        else:
            name = line.text.replace('\n', ' ').strip()
            articles.append(Article(number, name))
        current_number += 1

    result = []
    for i in articles:
        result.append(i.write_down())

    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([f"Число публикаций на elibrary.ru: {publications_total_elib}"])
        writer.writerow([f"Число публикаций в РИНЦ: {publications_rinc}"])
        writer.writerow([f"Число публикаций, входящих в ядро РИНЦ: {publications_rinc_core}"])
        for row in result:
            writer.writerow([row])

def main():
    for file in ["page.html", "result.csv"]:
        try:
            if os.path.exists(file):
                os.remove(file)
                print(f"Файл {file} удален.")
            else:
                print(f"Файл {file} не существует, пропускаем удаление.")
        except Exception as e:
            print(f"Ошибка при удалении файла {file}: {e}")
    loop_limit = 3
    loop_iteration = 0
    while loop_iteration < loop_limit:
        try:
            result = search_cycle()
            if result: # При успешном выполнении выйдет из цикла
                # Аня, я вернул тебе данные из search_cycle()
                publications_total_elib, publications_rinc, publications_rinc_core = result
                print("Функция search_cycle() завершена успешно.")
                print(f"Число публикаций на elibrary.ru: {publications_total_elib}\n"
                      f"Число публикаций в РИНЦ: {publications_rinc}\n"
                      f"Число публикаций, входящих в ядро РИНЦ: {publications_rinc_core}")
                parse_elibrary_html('page.html', 'result.csv', publications_total_elib, publications_rinc, publications_rinc_core)
                break
        except AuthorizationException as e:
            print(f"Ошибка авторизации: {e}")
        except AuthorTableMoreOneRow as e:
            print(f"Ошибка поиска авторов: {e}")
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
        loop_iteration += 1
    else:
        print(f"Достигнут лимит попыток ({loop_limit}).")
    #browser.quit()
    print("Программа выполнена.")


if __name__ == "__main__":
    main()

