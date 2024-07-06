import sqlite3

 # Открываем соединение с базой данных
conn = sqlite3.connect('mbr-base.db')
cursor = conn.cursor()
 # Читаем содержимое SQL-файла
with open('mbr-base.sql', 'r', encoding='utf-8') as file:
    sql_script = file.read()
 # Выполняем SQL-скрипт
cursor.executescript(sql_script)
 # Сохраняем изменения и закрываем соединение
conn.commit()
conn.close()
print("База данных успешно создана и заполнена данными из файла mbr-base.sql")