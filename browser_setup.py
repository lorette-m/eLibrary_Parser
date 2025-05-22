from selenium import webdriver
from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.firefox.options import Options
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

    browser = webdriver.Chrome(options=options)
    #browser = webdriver.Firefox(options=options)
    browser.set_window_size(*WINDOW_SIZE)
    browser.set_window_position(*WINDOW_POSITION)
    browser.get('https://www.elibrary.ru/authors.asp')

    return browser