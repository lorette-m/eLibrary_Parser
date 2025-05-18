from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from exceptions import AuthorizationException
from config import TEST_DATA

def authorize(browser):
    """
    Функция авторизации, вызывается если пользователь не авторизован (на странице обнаружен элемент с id 'win_login'). \n
    Запрашивает ввод данных, заполняет форму авторизациии, кликает на кнопку входа.
    """
    try:
        login_container = browser.find_element(By.ID, 'win_login')
        print("Пользователь не авторизован. Переходим к авторизации...")

        login_field = login_container.find_element(By.ID, 'login')
        password_field = login_container.find_element(By.ID, 'password')

        # user_login = input('Введите логин или почту: ')
        # user_password = input('Введите пароль: ')

        login_field.clear()
        login_field.send_keys(TEST_DATA['login'])
        password_field.clear()
        password_field.send_keys(TEST_DATA['password'])

        # Чекбокс "Запомнить меня"
        checkbox = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.NAME, 'knowme'))
        )
        if not checkbox.is_selected():
            checkbox.click()

        login_button = login_container.find_element(By.CLASS_NAME, 'butred')
        login_button.click()

        WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.ID, 'surname')))
        print("Авторизация выполнена.")
    except (TimeoutException, NoSuchElementException) as e:
        raise AuthorizationException("Не удалось авторизоваться. Проверьте элементы формы.") from e