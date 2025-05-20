import os
from browser_setup import setup_browser
from exceptions import AuthorizationException, AuthorTableMoreOneRow
from search_cycle import search_cycle
from html_parser import parse_elibrary_html
import glob
from pynput import keyboard
import sys

def cleanup_html():
    """Удаление сохраненных html страниц."""
    for file in glob.glob("page_*.html"):
        try:
            if os.path.exists(file):
                os.remove(file)
        except Exception as e:
            print(f"Ошибка при удалении файла {file}: {e}")

def cleanup_csv():
    """Удаление csv файлов с результатами парсинга."""
    csv_file = "result.csv"
    try:
        if os.path.exists(csv_file):
            os.remove(csv_file)
    except Exception as e:
        print(f"Ошибка при удалении файла {csv_file}: {e}")

def main():
    cleanup_html()
    cleanup_csv()
    browser = setup_browser()

    LOOP_LIMIT = 3
    loop_iteration = 0

    while loop_iteration < LOOP_LIMIT:
        try:
            result = search_cycle(browser)
            if result:
                publications_total_elib, publications_rinc, publications_rinc_core, total_pages = result

                for page in range(1, total_pages + 1):
                    parse_elibrary_html(f"page_{page}.html", 'result.csv',
                                        publications_total_elib, publications_rinc, publications_rinc_core,
                                        is_first_page=(page == 1))
                break
        except AuthorizationException as e:
            print(f"Ошибка авторизации: {e}")
        except AuthorTableMoreOneRow as e:
            print(f"Ошибка поиска авторов: {e}")
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
        loop_iteration += 1
    else:
        print(f"Достигнут лимит попыток ({LOOP_LIMIT}).")

    cleanup_html()
    # browser.quit()
    print("Программа выполнена.")
    print("Нажмите любую клавишу для завершения программы..")

    def on_press(key):
        return False

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

    browser.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
