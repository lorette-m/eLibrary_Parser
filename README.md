Elibrary Parser
==================================================================
Программа разработана для сбора информации о публикациях авторов в научных журналах.  
Для введенного автора (по ФИО или SPIN-коду) производится сбор и сохранение данных об общем количестве публикаций и самих статей в зависимости от выбранных категорий.
Данные сохраняются в формате CSV.  

The program is designed to collect information about the authors' publications in scientific journals.  
For the entered author (by full name or SPIN code), data on the total number of publications and the articles themselves is collected and saved, depending on the selected categories. The data is saved in CSV format.  

### Пример result.csv / output example:
![image](https://github.com/user-attachments/assets/6c6eaa6e-684b-46a4-8f6c-d8337e2431eb)

## Последний релиз / Last Release
Вы можете найти здесь https://github.com/lorette-m/eLibrary_Parser/releases/tag/v1.2  
В архиве присутствуют исполняемые файлы для работы через Chrome или Firefox, а также файл настройки конфигурации, где можно:  
1. включить режим отладки;  
2. автоматизировать авторизацию или поиск, заранее заполнив соответствующие поля;  
3. отключить GUI браузера (не рекомендуется из-за периодических тестов Тьюринга);
4. настроить располение открывающегося окна браузера.

Все исполняемые файлы собраны под Windows, x64

---
You can find it here https://github.com/lorette-m/eLibrary_Parser/releases/tag/v1.2
The archive contains executable files for working via Chrome or Firefox, as well as a configuration settings file where you can:
1. enable debugging mode;
2. automate authorization or search by filling in the appropriate fields in advance;
3. disable the browser GUI (not recommended due to periodic Turing tests);
4. adjust the location of the browser window that opens.

All executable files are built under Windows, x64

## via Yandex
В соседней ветке вы можете найти попытку запустить программу через Яндекс браузер (попытка неудачная). В качестве веб-драйвера использовался проект https://github.com/yandex/YandexDriver. Проект открыт для доработок.

In the next branch, you can find an attempt to launch the program via Yandex browser (the attempt was unsuccessful). The project was used as a web driver: https://github.com/yandex/YandexDriver. The project is open for improvements.
