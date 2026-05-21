# ТЕЛЕГРАММ БОТ ДЛЯ ОТСЛЕЖИВАНИЯ НАСТРОЕНИЯ ПОЛЬЗОВАТЕЛЯ

## ИНСТРУКЦИЯ ДЛЯ ЗАПУСКА БОТА

- Создать файл .env по примеру .env.пример и вставить данные
- Установить библиотеки из requirements.txt
- Заполнить базу данных командами: python -c "from db_handler import init_db; init_db()", sqlite3 database.db < test_data.sql
- Запустить файл bot.py