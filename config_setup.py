import json
import shutil
import textwrap
import os

def get_input(prompt, default):
    """
    Запрашивает у пользователя ввод y/n с заданным значением по умолчанию.
    Возвращает True для 'y' или False для 'n'.
    """
    while True:
        response = input(prompt).strip().lower()
        if response == '':
            return default.lower() == 'y'
        if response in ('y', 'n'):
            return response == 'y'
        print("Пожалуйста, введите 'y' или 'n'.")

def main():
    config = {}
    config_path = 'config.json'

    # Проверяем, существует ли config.json, и загружаем существующие данные
    existing_config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)
        except json.JSONDecodeError:
            print("Ошибка чтения config.json, создаём новый.")

    print("Отладка оптимального времени загрузки таблицы публикаций. \n\
При плохом интернет соединении и малом таймауте таблица публикаций может быть сохранена не полностью, поэтому если ваше интернет соединение \n\
медленное или нестабильное, лучше произведите настройку под свои условия. \n\
TIMEOUT = 10, оптимальное значение для быстрого интернет соединения. \n\
Инструкция по отладке: установите ARTICLES_TABLE_LOAD_DEBUG в True. Вывод отладки начнется после того, как вы выберете категории публикаций. \n\
Если три стабилизации показывают одно и то же значение, значит таблица успевает загрузиться. Если стабилизация возрастает, установите \n\
значение TIMEOUT больше, чтобы избежать проблемы при большем количестве статей в таблице. \n\
(максимум 100 на странице). Если после стабилизации происходит долгое ожидание, уменьшайте TIMEOUT.")

    config['ARTICLES_TABLE_LOAD_DEBUG'] = get_input(
        "Включить режим отладки времени загрузки? (y/N): ", default='n'
    )

    print("По умолчанию TIMEOUT = 10, оптимальное значение для быстрого интернет соединения.")
    timeout_temp = input("Введите значение TIMEOUT в секундах (Enter для пропуска): ")
    if timeout_temp == '':
        config['TIMEOUT'] = 10
    else:
        try:
            if int(timeout_temp) > 0:
                config['TIMEOUT'] = int(timeout_temp)
            else:
                print("Введено некорректное значение, TIMEOUT установлен по умолчанию.")
                config['TIMEOUT'] = 10
        except ValueError:
            print("Ошибка: нужно ввести целое положительное число. Установлено значение по умолчанию.")
            config['TIMEOUT'] = 10

    config['USE_LOGIN_FROM_CONFIG'] = get_input(
        "Использовать логин из конфигурации? Предпочтительно Y. (y/N): ", default='n'
    )
    if config['USE_LOGIN_FROM_CONFIG']:
        # Проверяем, есть ли существующие логин и пароль
        existing_login = existing_config.get('LOGIN_DATA', {}).get('login', '')
        existing_password = existing_config.get('LOGIN_DATA', {}).get('password', '')

        if existing_login and existing_password:
            print(f"Текущий логин: {existing_login}")
            print(f"Текущий пароль: {'*' * len(existing_password)}")  # Скрываем пароль
            keep_existing = get_input("Оставить текущие логин и пароль? (Y/n): ", default='Y')
            if keep_existing:
                config['LOGIN_DATA'] = {
                    'login': existing_login,
                    'password': existing_password
                }
            else:
                config['LOGIN_DATA'] = {
                    'login': input("Введите новый логин: "),
                    'password': input("Введите новый пароль: ")
                }
        else:
            config['LOGIN_DATA'] = {
                'login': input("Введите логин: "),
                'password': input("Введите пароль: ")
            }
    else:
        config['LOGIN_DATA'] = {'login': '', 'password': ''}

    config['USE_AUTHOR_FROM_CONFIG'] = get_input(
        "Использовать данные автора из конфигурации? (y/N): ", default='n'
    )

    if config['USE_AUTHOR_FROM_CONFIG']:
        config['AUTHOR_DATA'] = {
            'surname': input("Введите фамилию автора: "),
            'code': input("Введите SPIN-код автора: ")
        }
    else:
        config['AUTHOR_DATA'] = {'surname': '', 'code': ''}

    print("Окно браузера отображается, если установлен в True. \n\
Совет: лучше оставлять GUI включенным, т.к. периодически появляются тесты Тьюринга, которые необходимо решать, чтобы сайт работал \n\
при последующих запусках программы. Также включенный интерфейс позволяет сверить количество сохраненных статей.")

    config['BROWSER_GUI_ENABLED'] = get_input(
        "Включить GUI браузера? (Y/n): ", default='Y'
    )

    # Настройка WINDOW_SIZE
    existing_window_size = existing_config.get('WINDOW_SIZE', [768, 918])
    print(f"Текущий размер окна: {existing_window_size[0]}x{existing_window_size[1]}")
    keep_window_size = get_input("Оставить текущий размер окна? (Y/n): ", default='Y')
    if keep_window_size:
        config['WINDOW_SIZE'] = existing_window_size
    else:
        while True:
            try:
                width = int(input("Введите ширину окна (пиксели): "))
                height = int(input("Введите высоту окна (пиксели): "))
                config['WINDOW_SIZE'] = [width, height]
                break
            except ValueError:
                print("Пожалуйста, введите числовые значения.")

    # Настройка WINDOW_POSITION
    existing_window_position = existing_config.get('WINDOW_POSITION', [768, 0])
    print(f"Текущая позиция окна: X={existing_window_position[0]}, Y={existing_window_position[1]}")
    keep_window_position = get_input("Оставить текущую позицию окна? (Y/n): ", default='Y')
    if keep_window_position:
        config['WINDOW_POSITION'] = existing_window_position
    else:
        while True:
            try:
                x = int(input("Введите позицию X (пиксели): "))
                y = int(input("Введите позицию Y (пиксели): "))
                config['WINDOW_POSITION'] = [x, y]
                break
            except ValueError:
                print("Пожалуйста, введите числовые значения.")

    # Запись настроек в JSON-файл
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

    print("Настройки сохранены в config.json.")

if __name__ == "__main__":
    main()