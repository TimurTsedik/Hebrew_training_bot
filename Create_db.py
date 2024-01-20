import psycopg2


def create_tables(conn):
    # conn.cursor().execute("""
    # DROP TABLE IF EXISTS e_r_words CASCADE;
    # DROP TABLE IF EXISTS he_words CASCADE;
    # DROP TABLE IF EXISTS e_words CASCADE;
    # DROP TABLE IF EXISTS r_words CASCADE;
    # DROP TABLE IF EXISTS user_words;
    # DROP TABLE IF EXISTS users;
    # DROP TABLE IF EXISTS user_answers;
    # """)
    # conn.commit()
    #
    # conn.cursor().execute("""
    #         CREATE TABLE IF NOT EXISTS he_words(
    #             id integer PRIMARY KEY,
    #             word VARCHAR(20) NOT NULL,
    #             transcription VARCHAR(100) NOT NULL
    #         );
    #         """)
    # conn.cursor().execute("""
    #     CREATE TABLE IF NOT EXISTS e_words(
    #         id integer PRIMARY KEY,
    #         word VARCHAR(250) NOT NULL
    #     );
    #     """)
    # conn.cursor().execute("""
    #     CREATE TABLE IF NOT EXISTS r_words(
    #         id integer PRIMARY KEY,
    #         word VARCHAR(200) NOT NULL
    #     );
    #     """)
    # conn.cursor().execute("""
    #     CREATE TABLE IF NOT EXISTS e_r_words(
    #         id SERIAL PRIMARY KEY,
    #         e_word_id INTEGER NOT NULL REFERENCES e_words(id),
    #         r_word_id INTEGER NOT NULL REFERENCES r_words(id),
    #         he_word_id INTEGER NOT NULL REFERENCES he_words(id)
    #     );
    #     """)
    # conn.cursor().execute("""
    #     CREATE TABLE IF NOT EXISTS users(
    #         user_id INTEGER PRIMARY KEY,
    #         user_name VARCHAR(40) NOT NULL
    #     );
    #     """)
    # conn.cursor().execute("""
    #     CREATE TABLE IF NOT EXISTS user_words(
    #         id SERIAL PRIMARY KEY,
    #         user_id INTEGER NOT NULL REFERENCES users(user_id),
    #         custom_word_id INTEGER NOT NULL REFERENCES e_r_words(id)
    #     );
    #     """)
    #
    # cur.execute("""
    #     INSERT INTO r_words (id, word)
    #     VALUES (0, 'NO WORD');
    # """)

    conn.cursor().execute("""
        CREATE TABLE IF NOT EXISTS user_answers(
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(user_id),
            word_id INTEGER NOT NULL REFERENCES e_r_words(id),
            answer BOOLEAN NOT NULL
            )""")


with psycopg2.connect(database="telegram_hebrew", user="postgres", password="postgres") as conn:
    with conn.cursor() as cur:
        create_tables(conn)
    conn.commit()



