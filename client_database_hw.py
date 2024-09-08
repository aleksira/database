import psycopg2


# Создание таблицы:
def create_table(conn):
    conn.cursor().execute('''
        CREATE TABLE IF NOT EXISTS client(
            id SERIAL PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT
        );
        ''')
    conn.commit()


# Добавление нового клиента:
def new_client(conn, first_name, last_name, email, phones=None):
    conn.cursor().execute('''
        INSERT INTO client(first_name, last_name, email, phone)
        VALUES(%s, %s, %s, %s);
        ''', (first_name, last_name, email, phones))
    conn.commit()


# Добавление телефона по id клиента:
def add_phone(conn, phone, client_id):
    conn.cursor().execute('''
        UPDATE client SET phone=%s WHERE id=%s;
        ''', (phone, client_id))
    return conn.commit()


# Вспомогательная функция: возвращает информацию из запрашиваемого столбика по id клиента
def info_by_id(conn, client_id, requested):
    conn.cursor().execute('''
        SELECT %s FROM client
        WHERE id=%s;
        ''', (requested, client_id))
    return conn.cursor().fetchone()[0]


# Изменение информации: если какой-либо из параметров не задан, ему присваивается уже существующее значение,
# т.к. изменяются все параметры
def change_info(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    if first_name is None:
        first_name = info_by_id(conn, client_id, 'first_name')
    if last_name is None:
        last_name = info_by_id(conn, client_id, 'last_name')
    if email is None:
        email = info_by_id(conn, client_id, 'email')
    if phones is None:
        phones = info_by_id(conn, client_id, 'phone')
    conn.cursor().execute('''
        UPDATE client SET first_name=%s, last_name=%s, email=%s, phone=%s WHERE id=%s;
        ''', (first_name, last_name, email, phones, client_id))
    conn.commit()

# Удаление телефона:
def delete_phone(conn, client_id, phone):
    # сначала получаем уже имеющуюся информацию о телефонах
    conn.cursor().execute('''
        SELECT phone
        FROM client
        WHERE id=$s;
        ''', (client_id,))
    phones = conn.cursor().fetchone()[0]

    # перезаписываем строку с телефонами
    if phone in phones:
        phones.replace(phone, '')

    # обновляем информацию в базе данных
    conn.cursor().execute('''
        UPDATE client
        SET phone=%s
        WHERE id=%s;
        ''', (phones, client_id))
    conn.commit()


# Удаление клиента по id
def delete_client(conn, client_id):
    conn.cursor().execute('''
        DELETE FROM client
        WHERE id=%s;
        ''', (client_id,))
    conn.commit()


# Поиск id клиента по его данным:
def find_client(conn, first_name=None, last_name=None, email=None, phones=None):
    if first_name is not None:
        conn.cursor().execute('''
            SELECT id
            FROM client
            WHERE first_name=%s;
            ''', (first_name,))
        client_id = conn.cursor().fetchone()[0]

    elif last_name is not None:
        conn.cursor().execute('''
            SELECT id
            FROM client
            WHERE last_name=%s;
            ''', (last_name,))
        client_id = conn.cursor().fetchone()[0]

    elif email is not None:
        conn.cursor().execute('''
            SELECT id
            FROM client
            WHERE email=%s;
            ''', (email,))
        client_id = conn.cursor().fetchone()[0]

    elif phones is not None:
        conn.cursor().execute('''
            SELECT id
            FROM client
            WHERE phone LIKE f'%{%s}%';
            ''', (phones,))
        client_id = conn.cursor().fetchone()[0]

    else:
        client_id = 'not found'
    return client_id


# Реализация функций:
with psycopg2.connect(database='clients', user='postgres', password='gottawork') as conn:
    conn.cursor().execute('''
        DROP TABLE IF EXISTS client;
        ''')
    conn.commit()

    create_table(conn)
    new_client(conn, 'Albert', 'Brown', 'alb@em.com', '1234567')
    new_client(conn, 'Robert', 'Lee', 'rob@em.com')
    add_phone(conn, '098890', 2)
    change_info(conn, 1, email='alb02@em.com')
    delete_phone(conn, 1, '1234567')
    delete_client(conn, 1)
    robert_id = find_client(conn, first_name='Robert')
    print(robert_id)

conn.close()