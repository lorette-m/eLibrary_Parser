from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from exceptions import AuthorizationException, AuthorTableMoreOneRow
from config import TEST_DATA
from authorization import authorize

def search_cycle(browser):
    """Основная функция работы с сайтом"""
    try:
        if browser.current_url != 'https://www.elibrary.ru/authors.asp':
            browser.get('https://www.elibrary.ru/authors.asp')
            print("Перешли на начальную страницу.")

        if len(browser.window_handles) > 1:
            for window_handle in browser.window_handles[1:]:
                browser.switch_to.window(window_handle)
                browser.close()
            browser.switch_to.window(browser.window_handles[0])
            print("Закрыты лишние вкладки.")

        try:
            browser.find_element(By.ID, 'win_login')
            authorize(browser)
        except NoSuchElementException:
            print("Пользователь уже авторизован.")

        surname_field = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.ID, 'surname'))
        )
        surname_field.clear()
        code_field = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.ID, 'codevalue'))
        )
        code_field.clear()

        surname_field.send_keys(TEST_DATA['surname'])
        code_field.send_keys(TEST_DATA['code'] + Keys.RETURN)

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

        authors_table = WebDriverWait(browser, 15).until(
            EC.presence_of_element_located((By.ID, 'restab'))
        )
        rows_in_table = authors_table.find_elements(By.TAG_NAME, 'tr')
        print(f"Найдено строк в таблице: {len(rows_in_table)}")
        if len(rows_in_table) > 4:
            raise AuthorTableMoreOneRow()

        statistical_page = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//a[contains(@href, "author_profile.asp?id=") and contains(@title, "Анализ публикационной активности")]'
            ))
        )
        statistical_page.click()
        print("Страница статистики загружена.")

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

        for category in categories:
            checkbox = WebDriverWait(browser, 5).until(
                EC.element_to_be_clickable((By.ID, category["id"]))
            )
            if checkbox.is_selected():
                checkbox.click()

        print("Выберите категории публикаций (введите номера через пробел, например: 1 3 5):")
        for i, category in enumerate(categories, 1):
            print(f"{i}. {category['name']}")

        selected_indices = input("Ваш выбор: ").split(" ")
        selected_indices = [int(i.strip()) - 1 for i in selected_indices if i.strip().isdigit()]

        if not selected_indices or max(selected_indices) >= len(categories) or min(selected_indices) < 0:
            print("Неверный выбор категорий.")
            return None

        for index in selected_indices:
            checkbox_id = categories[index]["id"]
            checkbox = WebDriverWait(browser, 15).until(
                EC.element_to_be_clickable((By.ID, checkbox_id))
            )
            if not checkbox.is_selected():
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
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.ID, 'restab')))

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