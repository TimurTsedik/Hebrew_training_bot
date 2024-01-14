import psycopg2

def create_initial_content():
    with psycopg2.connect(database="telegram_hebrew", user="postgres", password="postgres") as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO e_words (word)
                VALUES 
                ('Car'),
                ('Green'),
                ('White'),
                ('Peace'),
                ('Apple'),
                ('Orange'),
                ('Water'),
                ('Milk'),
                ('Banana'),
                ('Hello'),
                ('World')
                ;
            """)
            cur.execute("""
                INSERT INTO r_words (word)
                VALUES 
                ('Машина'),
                ('Зеленый'),
                ('Белый'),
                ('Мир'),
                ('Яблоко'),
                ('Апельсин'),
                ('Вода'),
                ('Молоко'),
                ('Банан'),
                ('Привет')
                ;
            """)
            cur.execute("""
                INSERT INTO e_r_words (e_word_id, r_word_id)
                VALUES 
                (1, 1),
                (2, 2),
                (3, 3),
                (4, 4),
                (5, 5),
                (6, 6),
                (7, 7),
                (8, 8),
                (9, 9),
                (10, 10),
                (11, 4)
                ;
            """)
            conn.commit()


def read_dict_from_file_to_db():
    f = open('dict.csv', 'r')
    lines = f.readlines()
    for line in lines:
        line = line.split(';')
        with psycopg2.connect(database="telegram_hebrew", user="postgres", password="postgres") as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO e_words (word)
                    VALUES (%s) returning id
                    """, (line[1],))
                e_word_id = cur.fetchone()[0]
                cur.execute("""
                    INSERT INTO r_words (word)
                    VALUES (%s) returning id
                    """, (line[0],))
                r_word_id = cur.fetchone()[0]
                cur.execute("""
                    INSERT INTO e_r_words (e_word_id, r_word_id)
                    VALUES (%s, %s)
                    """, (e_word_id, r_word_id))
                conn.commit()
    f.close()

read_dict_from_file_to_db()