import json

# Значения по умолчанию, взятые из текущего config.py
DEFAULT_CONFIG = {
    'ARTICLES_TABLE_LOAD_DEBUG': False,
    'TIMEOUT': 10,
    'USE_LOGIN_FROM_CONFIG': True,
    'LOGIN_DATA': {'login': '', 'password': ''},
    'USE_AUTHOR_FROM_CONFIG': False,
    # Автор для примера
    'AUTHOR_DATA': {'surname': 'Воронков', 'code': '9914-6861'},
    'BROWSER_GUI_ENABLED': True,
    'WINDOW_SIZE': [768, 918],
    'WINDOW_POSITION': [768, 0]
}

# Чтение конфигурации из JSON
try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    config = DEFAULT_CONFIG

ARTICLES_TABLE_LOAD_DEBUG = config.get('ARTICLES_TABLE_LOAD_DEBUG', DEFAULT_CONFIG['ARTICLES_TABLE_LOAD_DEBUG'])
"""
Отладка оптимального времени загрузки таблицы публикаций. 
При плохом интернет соединении и малом таймауте таблица публикаций может быть сохранена не полностью, 
поэтому если ваше интернет соединение медленное или нестабильное, лучше произведите настройку под свои условия. \n
TIMEOUT = 10, оптимальное значение для быстрого интернет соединения. \n
Инструкция по отладке: установите ARTICLES_TABLE_LOAD_DEBUG в True. 
Вывод отладки начнется после того, как вы выберете категории публикаций.
Если три стабилизации показывают одно и то же значение, значит таблица успевает загрузиться.
Если стабилизация возрастает, установите значение TIMEOUT больше, 
чтобы избежать проблемы при большем количестве статей в таблице (максимум 100 на странице).
Если после стабилизации происходит долгое ожидание, уменьшайте TIMEOUT.
"""
TIMEOUT = config.get('TIMEOUT', DEFAULT_CONFIG['TIMEOUT'])
"""TIMEOUT = 10, оптимальное значение для загрузки 100 строк таблицы при быстром интернет соединении."""

USE_LOGIN_FROM_CONFIG = config.get('USE_LOGIN_FROM_CONFIG', DEFAULT_CONFIG['USE_LOGIN_FROM_CONFIG'])
"""
True: при авторизации на elibrary.ru используется логин и пароль из LOGIN_DATA в config.py. \n
False: перед авторизацией пользователю необходимо ввести логин и пароль в консоли. \n
Примечание: авторизация происходит при каждом запуске программы.
"""

LOGIN_DATA = config.get('LOGIN_DATA', DEFAULT_CONFIG['LOGIN_DATA'])

USE_AUTHOR_FROM_CONFIG = config.get('USE_AUTHOR_FROM_CONFIG', DEFAULT_CONFIG['USE_AUTHOR_FROM_CONFIG'])
"""
True: проивзодит поиск по автору, фамилия и SPIN-код которого указаны в AUTHOR_DATA в config.py. \n
False: пользователю необходимо ввести имя автора и SPIN-код в консоли.
"""

AUTHOR_DATA = config.get('AUTHOR_DATA', DEFAULT_CONFIG['AUTHOR_DATA'])

BROWSER_GUI_ENABLED = config.get('BROWSER_GUI_ENABLED', DEFAULT_CONFIG['BROWSER_GUI_ENABLED'])
"""
Окно браузера отображается, если установлен в True. \n
Совет: лучше оставлять GUI включенным, т.к. периодически появляются тесты Тьюринга, которые необходимо решать, 
чтобы сайт работал при последующих запусках программы. Также включенный интерфейс позволяет сверить количество сохраненных статей.
"""

# Размер и позиция для правой половины экрана (1920x1200, масштаб 125%)
WINDOW_SIZE = tuple(config.get('WINDOW_SIZE', DEFAULT_CONFIG['WINDOW_SIZE']))
WINDOW_POSITION = tuple(config.get('WINDOW_POSITION', DEFAULT_CONFIG['WINDOW_POSITION']))