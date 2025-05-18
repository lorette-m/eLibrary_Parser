import os
from browser_setup import setup_browser
from exceptions import AuthorizationException, AuthorTableMoreOneRow
from search_cycle import search_cycle
from html_parser import parse_elibrary_html
from config import LOOP_LIMIT

def cleanup_files():
    """Удаление временных файлов"""
    for file in ["page.html", "result.csv"]:
        try:
            if os.path.exists(file):
                os.remove(file)
                print(f"Файл {file} удален.")
            else:
                print(f"Файл {file} не существует, пропускаем удаление.")
        except Exception as e:
            print(f"Ошибка при удалении файла {file}: {e}")

def main():
    cleanup_files()
    browser = setup_browser()
    
    loop_iteration = 0
    while loop_iteration < LOOP_LIMIT:
        try:
            result = search_cycle(browser)
            if result:
                publications_total_elib, publications_rinc, publications_rinc_core = result
                print("Функция search_cycle() завершена успешно.")
                print(f"Число публикаций на elibrary.ru: {publications_total_elib}\n"
                      f"Число публикаций в РИНЦ: {publications_rinc}\n"
                      f"Число публикаций, входящих в ядро РИНЦ: {publications_rinc_core}")
                
                parse_elibrary_html('page.html', 'result.csv', 
                                  publications_total_elib, publications_rinc, publications_rinc_core)
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
    
    # browser.quit()
    print("Программа выполнена.")

if __name__ == "__main__":
    main()
