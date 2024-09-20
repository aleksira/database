import psycopg2


# Создание таблицы клиентов и связанной с ней таблицы телефонов:
def create_table(conn):
    conn.cursor().execute('''
        CREATE TABLE IF NOT EXISTS client(
            id SERIAL PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS phones(
            id SERIAL PRIMARY KEY,
            phone VARCHAR(40) UNIQUE,
            client_id INTEGER NOT NULL REFERENCES client(id)
        );
        ''')
    pass


# Добавление нового клиента:
def new_client(conn, first_name, last_name, email):
    conn.cursor().execute('''
        INSERT INTO client(first_name, last_name, email)
        VALUES(%s, %s, %s);
        ''', (first_name, last_name, email))
    pass


# Добавление телефона по id клиента:
def add_phone(conn, phone, client_id):
    conn.cursor().execute('''
        INSERT INTO phones(phone, client_id)
        VALUES(%s, %s);
        ''', (phone, client_id))
    pass


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
    if phones is not None:
        conn.cursor.execute('''
            UPDATE phones SET phone=%s WHERE client_id=%s;
        ''', (phones, client_id))
    conn.cursor().execute('''
        UPDATE client SET first_name=%s, last_name=%s, email=%s WHERE id=%s;
        ''', (first_name, last_name, email, client_id))
    pass


# Удаление телефона:
def delete_phone(conn, client_id, phone):
    conn.cursor.execute('''
        DELETE FROM phones
        WHERE phone=%s and client_id=%s;
    ''', (phone, client_id))
    pass


# Удаление клиента по id
def delete_client(conn, client_id):
    conn.cursor().execute('''
        DELETE FROM client
        WHERE id=%s;
        ''', (client_id,))
    pass


# Поиск id клиента по его данным:
def find_client(conn, first_name=None, last_name=None, email=None, phones=None):
    if first_name is None:
        first_name = '%'
    if last_name is None:
        last_name = '%'
    if email is None:
        email = '%'

    conn.cursor.execute('''
        SELECT id FROM client
        WHERE first_name LIKE %s AND last_name LIKE %s AND email LIKE %s;
    ''', (first_name, last_name, email))

    client_id = conn.cursor.fetchall()

    if phones is not None:
        conn.cursor.execute('''
            SELECT client_id from phones
            WHERE phone=%s;
        ''', (phones,))
        client_id = conn.cursor().fetchall()

    return client_id


# Реализация функций:
if __name__ == '__main__':
    with psycopg2.connect(database='clients', user='postgres', password='gottawork') as conn:
        conn.cursor().execute('''
            DROP TABLE IF EXISTS client;
            DROP TABLE IF EXISTS phones;
            ''')
        conn.commit()

        create_table(conn)
        new_client(conn, 'Albert', 'Brown', 'alb@em.com')
        new_client(conn, 'Robert', 'Lee', 'rob@em.com')
        add_phone(conn, '1323332', 1)
        add_phone(conn, '098890', 2)
        change_info(conn, 1, email='alb02@em.com')
        delete_phone(conn, 2, '098890')
        delete_client(conn, 1)
        robert_id = find_client(conn, first_name='Robert')
        print(robert_id)

    conn.close()
