from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from fake_useragent import UserAgent
from config import WINDOW_SIZE, WINDOW_POSITION, BASE_URL


def setup_browser():
    """Настройка и возврат экземпляра браузера"""
    ua = UserAgent()
    options = Options()
    options.add_argument("--disable-infobars")
    options.add_argument(f"--user-agent={ua.random}")

    browser = webdriver.Firefox(options=options)
    browser.set_window_size(*WINDOW_SIZE)
    browser.set_window_position(*WINDOW_POSITION)
    browser.get(BASE_URL)

    return browser