from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent
from config import WINDOW_SIZE, WINDOW_POSITION, BROWSER_GUI_ENABLED


def setup_browser():
    """Настройка бразуера, user agent'а и окна. Данные из config.py."""
    ua = UserAgent()
    options = Options()

    if not BROWSER_GUI_ENABLED:
        options.add_argument("--headless")

    options.add_argument("--disable-infobars")
    options.add_argument(f"--user-agent={ua.random}")

    # browser = webdriver.Firefox(options=options)
    #browser = webdriver.Chrome(options=options)
    binary_yandex_driver_file = "C:/Utilities/yandexdriver-25.4.0.1973-win64/yandexdriver.exe"  # path to YandexDriver
    yandex_driver_path = "C:/Utilities/yandexdriver-25.4.0.1973-win64/yandexdriver.exe"

    # Используем Service для инициализации драйвера
    service = Service(executable_path=yandex_driver_path)
    browser = webdriver.Chrome(service=service, options=options)
    #browser = webdriver.Chrome(binary_yandex_driver_file, options=options)

    browser.set_window_size(*WINDOW_SIZE)
    browser.set_window_position(*WINDOW_POSITION)
    browser.get('https://www.elibrary.ru/authors.asp')

    return browser