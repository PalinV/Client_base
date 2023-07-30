from genericpath import exists
import psycopg2


def create_table_client(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS client(
        id SERIAL PRIMARY KEY,
        first_name VARCHAR(40) NOT NULL,
        last_name VARCHAR(60) NOT NULL,
        email VARCHAR(60) UNIQUE
        ); 
            
    CREATE TABLE IF NOT EXISTS phone_number(
        id SERIAL PRIMARY KEY,
        number VARCHAR(11) UNIQUE,
        client_id INTEGER NOT NULL REFERENCES client(id)
    ); 
    """)
    conn.commit()


def print_data(res):
    print('Найдено: \n')
    for client in res:
        print(' '.join(client))


def get_client_data():
    f_name = input('Ведите имя клиента: ')
    l_name = input('Ведите фамилию клиента: ')
    mail = input('Ведите e_mail клиента: ')
    client_data = (f_name, l_name, mail)
    return client_data


def get_client_id(cursor):
    client_data = get_client_data()
    cursor.execute("""
    SELECT id FROM client
    WHERE first_name = %s and last_name = %s and email = %s;
        """,(client_data))            
    id = cursor.fetchone() 
    return id


def search_client_by_name(cursor, f_name, l_name):
    cursor.execute("""
    SELECT first_name, last_name, email, p.number FROM client AS c
    JOIN phone_number AS p on c.id = p.client_id
    WHERE  first_name = %s and  last_name = %s;             
    """,(f_name, l_name))
    return cursor.fetchall()


def search_client_by_mail(cursor, mail):
    cursor.execute("""
    SELECT first_name, last_name, email, p.number FROM client AS c
    JOIN phone_number AS p on c.id = p.client_id
    WHERE  email = %s ;             
    """,(mail,))
    return cursor.fetchall()


def search_client_by_phone(cursor, phone):
    cursor.execute("""
    SELECT first_name, last_name, email, p.number FROM client AS c
    JOIN phone_number AS p on c.id = p.client_id
    WHERE  p.number = %s ;             
    """,(phone,))
    return cursor.fetchall()


def add_client(cursor, first_name, last_name, e_mail):
    p_number = int(input('Ведите номер телефона клиента: '))
    cursor.execute("""
    INSERT INTO client(first_name, last_name, email)
        VALUES (%s,%s,%s) returning id;""",(first_name, last_name, e_mail))
    id = cur.fetchone()[0]
    cursor.execute("""
    INSERT INTO phone_number(number, client_id)
        VALUES (%s,%s) returning id;""",(p_number, id))
    conn.commit()


def add_number(cursor, id):
    p_number = int(input('Ведите новый номер телефона клиента: '))
    cursor.execute("""
    INSERT INTO phone_number(number, client_id)
        VALUES (%s,%s) returning id;""",(p_number, id))
    conn.commit()


def change_client_data(cursor):
    print('Укажите клиента данные которого будут меняться')
    client_id = get_client_id(cursor)
    print('Выберите один из пунктов:\n'
          '1. Меняем имя клиента\n'
          '2. Меняем фамилию клиента\n'
          '3. Меняем email клиента')
    choice = input()
    if choice == '1':
        new_first_name = input('Введите новое имя клиента: \n')
        cursor.execute("""
        UPDATE client SET first_name = %s
        WHERE id = %s
        """,(new_first_name, client_id))
    elif choice == '2':
        new_last_name = input('Введите новую фамилию клиента: \n')
        cursor.execute("""
        UPDATE client SET last_name = %s
        WHERE id = %s 
        """, (new_last_name, client_id))
    elif choice == '3':
        new_mail_name = input('Введите новый email клиента: \n')
        cursor.execute("""
        UPDATE client SET email = %s
        WHERE id = %s 
        """, (new_mail_name, client_id))
    conn.commit()    


def delete_number(cursor, id):
    cursor.execute("""
    SELECT number FROM phone_number
    WHERE client_id = %s
    """,(id))
    for number in cur.fetchall():
        num = ''.join(number)
        print(f'Удалить номер {num}? Y/N')
        if input().upper() == 'Y':
            break
    cursor.execute("""
    DELETE FROM phone_number
        WHERE number = %s;""",(number,))
    conn.commit()


def delete_client(cursor, id):
    cursor.execute("""
    DELETE FROM phone_number
    WHERE client_id = %s  
    """,(id))
    cursor.execute("""
    DELETE FROM client
        WHERE id = %s
    """,(id))
    conn.commit()

def search_client(cur):
    print('Выберите один из пунктов:\n'
          '1. Найти по имени и фамилии\n'
          '2. Найти по email\n'
          '3. Найти по телефону')
    choice = input('Выберите операцию: \n')
    if choice == '1':
        f_name = input('Ведите имя клиента: ')
        l_name = input('Ведите фамилию клиента: ')
        res = search_client_by_name(cur, f_name, l_name)
    elif choice == '2':
        mail = input('Ведите e_mail клиента: ')
        res = search_client_by_mail(cur, mail)
    elif choice == '3':
        p_number = str(input('Ведите номер телефона клиента: '))
        res = search_client_by_phone(cur, p_number)
    print_data(res)
    input('Для продолжения нажмите любую клавишу')


with psycopg2.connect(database='client_db', user='postgres', password='16') as conn:
    with conn.cursor() as cur:
        create_table_client(cur)
        while True:
            print('Выберите один из пунктов:\n'
                  '1. Добавить нового клиента\n'
                  '2. Добавить телефонный номер у существующего клиента\n'
                  '3. Изменить данные у клиента\n'
                  '4. Удалить телефон для существующего клиента\n'
                  '5. Удалить существующего клиента\n'
                  '6. Найти клиента по его данным: имени, фамилии, email или телефону\n'
                  '7. Выход')
            choice = input('Выберите операцию: \n')
            try:
                if choice == '1':
                    add_client(cur, *get_client_data())
                elif choice == '2':
                    add_number(cur, get_client_id(cur))
                elif choice == '3':
                    change_client_data(cur)
                elif choice == '4':
                    delete_number(cur, get_client_id(cur))
                elif choice == '5':
                    delete_client(cur, get_client_id(cur))
                elif choice == '6':
                    search_client(cur)
                elif choice == '7':
                    break
            except:
                input("\nДанные клиента были внесены не верно !!!!\n"
                      "Нажмите любую клавишу для продолжения\n")
conn.close()
