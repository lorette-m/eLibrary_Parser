import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from exceptions import AuthorizationException, AuthorTableMoreOneRow
from config import ARTICLES_TABLE_LOAD_DEBUG, TIMEOUT, AUTHOR_DATA, USE_AUTHOR_FROM_CONFIG
from authorization import authorize

def search_cycle(browser):
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

        try:
            browser.find_element(By.ID, 'win_login')
            authorize(browser)
        except NoSuchElementException:
            print("Пользователь авторизован.")

        surname_field = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.ID, 'surname'))
        )
        surname_field.clear()
        code_field = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.ID, 'codevalue'))
        )
        code_field.clear()

        if USE_AUTHOR_FROM_CONFIG:
            surname = AUTHOR_DATA['surname']
            code = AUTHOR_DATA['code']
        else:
            print("Примечание: если не знаете SPIN-код, можете ввести ФИО — программа сработает если будет найдено не более одного автора.")
            surname = input("Введите фамилию автора: ")
            code = input("Введите SPIN-код: ")

        surname_field.send_keys(surname)
        code_field.send_keys(code + Keys.RETURN)

        share = WebDriverWait(browser, 10).until(
           EC.element_to_be_clickable((By.CLASS_NAME, 'butred'))
        )
        share.click()

        try:
            WebDriverWait(browser, 5).until(EC.alert_is_present())
            alert_present = True
        except TimeoutException:
            alert_present = False

        if alert_present:
            alert = browser.switch_to.alert
            print("Alert text:", alert.text)
            alert.dismiss()
            raise AuthorizationException("Ошибка авторизации. Для парсинга необходимо авторизироваться в eLibrary")

        ### Работа с таблицей авторов

        authors_table = WebDriverWait(browser, 15).until(
            EC.presence_of_element_located((By.ID, 'restab'))
        )
        rows_in_table = authors_table.find_elements(By.TAG_NAME, 'tr')
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

        publications_total_elib = WebDriverWait(browser, 15).until(
            EC.presence_of_element_located((
                By.XPATH,
                '//a[contains(@href, "author_items.asp") and contains(@title, "Полный список публикаций")]'
            ))
        ).text

        publications_rinc = WebDriverWait(browser, 15).until(
            EC.presence_of_element_located((
                By.XPATH,
                '//a[contains(@href, "author_items.asp") and contains(@title, "Список публикаций автора в РИНЦ")]'
            ))
        ).text

        publications_rinc_core = WebDriverWait(browser, 15).until(
            EC.presence_of_element_located((
                By.XPATH,
                '//a[contains(@href, "author_items.asp") and contains(@title, "Список публикаций автора, входящих в ядро РИНЦ")]'
            ))
        ).text

        browser.back()

        ### Переходим на страницу с публикациями в РИНЦ

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

        WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        types_header = WebDriverWait(browser, 30).until(
            EC.element_to_be_clickable((By.ID, 'hdr_types'))
        )
        types_header.click()

        time.sleep(2)

        checkbox_articles = WebDriverWait(browser, 30).until(
            EC.element_to_be_clickable((By.ID, 'types_RAR'))
        )
        checkbox_articles.click()

        cats_header = WebDriverWait(browser, 60).until(
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

        # Сайт иногда сохраняет состояние чекбоксов, нужно пройтись и проверить, что галочек нет
        for category in categories:
            checkbox = WebDriverWait(browser, 30).until(
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
            return None

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
        WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.ID, 'restab')))

        ### Определяем количество страниц
        try:
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "pages")))
            pages_panel = browser.find_element(By.ID, "pages")
            page_links = pages_panel.find_elements(By.TAG_NAME, "a")
            page_numbers = []
            for link in page_links:
                href = link.get_attribute('href')
                if href and 'goto_page' in href:
                    match = re.search(r'goto_page\((\d+)\)', href)
                    if match:
                        page_numbers.append(int(match.group(1)))
            total_pages = max(page_numbers) if page_numbers else 1
        except TimeoutException:
            total_pages = 1
        except NoSuchElementException:
            total_pages = 1

        ### Сохранение всех страниц
        for page in range(1, total_pages + 1):
            if page > 1:
                try:
                    pages_panel = browser.find_element(By.ID, "pages")
                    next_page_link = pages_panel.find_element(By.XPATH, f".//a[contains(@href, 'goto_page({page})')]")
                    browser.execute_script("arguments[0].click();", next_page_link)
                    WebDriverWait(browser, 15).until(EC.staleness_of(browser.find_element(By.ID, 'restab')))
                    WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.ID, 'restab')))
                    WebDriverWait(browser, 30).until(
                        EC.presence_of_element_located((By.XPATH, f"//div[@id='pages']//font[text()='{page}']"))
                    )
                except Exception as e:
                    print(f"Ошибка при переходе на страницу {page}: {e}")
                    break

            if ARTICLES_TABLE_LOAD_DEBUG:
                start_time = time.time()
                poll_frequency = 1
                stable_threshold = 3
                last_row_count = 0
                stable_count = 0

                while time.time() - start_time < TIMEOUT:
                    rows = browser.find_elements(By.XPATH, "//table[@id='restab']//tr[@valign='middle']")
                    current_row_count = len(rows)
                    print(f"Текущее количество строк на странице {page}: {current_row_count}")
                    if current_row_count == last_row_count:
                        stable_count += 1
                        if stable_count >= stable_threshold:
                            print(f"Таблица стабилизировалась с {current_row_count} строками на странице {page}")
                            break
                    else:
                        stable_count = 0
                    last_row_count = current_row_count
                    time.sleep(poll_frequency)
            else:
                time.sleep(TIMEOUT)

            with open(f"page_{page}.html", "w", encoding="utf-8") as f:
                f.write(browser.page_source)

        return publications_total_elib, publications_rinc, publications_rinc_core, total_pages

    except AuthorizationException:
        raise
    except AuthorTableMoreOneRow:
        raise
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        browser.get('https://www.elibrary.ru/authors.asp')
        print("Перешли на начальную страницу из-за ошибки.")
        raise