from bs4 import BeautifulSoup
import csv
from exceptions import AuthorizationException, AuthorTableMoreOneRow

def parse_elibrary_html(html_path, csv_path, publications_total_elib, publications_rinc, publications_rinc_core):
    """Парсинг сохранённой веб-страницы со списком статей"""
    try:
        with open(html_path, encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f, 'html.parser')
    except Exception as e:
        raise ValueError(f"Ошибка при чтении файла {html_path}: {e}")

    table = soup.find('table', id='restab')
    if not table:
        raise ValueError("Таблица с id='restab' не найдена в HTML.")

    rows = table.find_all('tr', attrs={'valign': 'middle'})
    if not rows:
        raise ValueError("Строки таблицы не найдены.")

    articles = []
    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 3:
            continue

        number_cell = cells[0].find('font', color="#00008f")
        number = number_cell.find('b').text.strip() if number_cell and number_cell.find('b') else ''
        if number.endswith('.'):
            number = number[:-1].strip()

        info_cell = cells[1]
        title = ''
        title_tag = info_cell.find('a', href=lambda x: x and '/item.asp?id=' in x)
        if title_tag and title_tag.find('b'):
            title = title_tag.find('b').text.strip()
        else:
            alt_title_tag = info_cell.find('b')
            if alt_title_tag and alt_title_tag.find('font', color="#00008f"):
                title = alt_title_tag.find('font', color="#00008f").text.strip()

        authors = ''
        font_tags = info_cell.find_all('font', color="#00008f")
        for font_tag in font_tags:
            authors_tag = font_tag.find('i')
            if authors_tag:
                authors = authors_tag.text.strip()
                break

        journal = ''
        additional_info = ''
        for font_tag in font_tags:
            journal_tag = font_tag.find('a', href=lambda x: x and ('contents.asp?id=' in str(x) or 'contents.asp?titleid=' in str(x)) and '&selid' not in str(x))
            if journal_tag:
                journal = journal_tag.text.strip()
                full_text = font_tag.get_text(separator=" ").strip()
                journal_text = journal_tag.text.strip()
                start_pos = full_text.find(journal_text) + len(journal_text)
                additional_info = full_text[start_pos:].strip()
                additional_info = additional_info.strip('. ')
                break

        if journal or authors or title or additional_info:
            articles.append({
                'number': number,
                'authors': authors,
                'title': title,
                'journal': journal,
                'additional_info': additional_info
            })

    if not articles:
        print("Внимание: не удалось извлечь ни одной статьи из таблицы.")

    try:
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([f"Число публикаций на elibrary.ru: {publications_total_elib}"])
            writer.writerow([f"Число публикаций в РИНЦ: {publications_rinc}"])
            writer.writerow([f"Число публикаций, входящих в ядро РИНЦ: {publications_rinc_core}"])
            writer.writerow([])
            writer.writerow(['Номер', 'Авторы', 'Название', 'Журнал', 'Дополнительная информация'])
            for article in articles:
                writer.writerow([
                    article['number'],
                    article['authors'],
                    article['title'],
                    article['journal'],
                    article['additional_info']
                ])
        print(f"Данные сохранены в {csv_path}. Найдено {len(articles)} статей.")
    except Exception as e:
        raise ValueError(f"Ошибка при записи в файл {csv_path}: {e}")