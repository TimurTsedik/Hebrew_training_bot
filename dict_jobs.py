import psycopg2


class PostgreSQL:

    def __init__(self):
        self.database = 'telegram_hebrew'
        self.login = 'postgres'
        self.password = 'postgres'


    def random_word_from_base(self, user_id, mistakes: bool):
        with psycopg2.connect(database=self.database, user=self.login, password=self.password) as conn:
            with conn.cursor() as cur:
                try:
                    if mistakes:
                        cur.execute("""
                        SELECT hw.word as h_w, rw.word as r_w, hw.transcription as h_t, ew.word as e_w, erw.id as erw_id
                            from he_words hw
                            join e_r_words erw on erw.r_word_id = hw.id 
                            join r_words rw on rw.id = erw.r_word_id
                            join e_words ew on ew.id = erw.e_word_id
                            full outer join user_words uw on uw.custom_word_id = erw.id
                            join user_answers ua on erw.e_word_id = ua.id
                            where (uw.user_id = %s or uw.user_id is null)
                            and erw.id in (select word_id from user_answers where answer = false limit 200)
                            ORDER BY random() DESC
                            LIMIT 1;
                        """, (user_id,))
                    else:
                        cur.execute("""
                        SELECT hw.word as h_w, rw.word as r_w, hw.transcription as h_t, ew.word as e_w, erw.id as erw_id
                            from he_words hw
                            join e_r_words erw on erw.r_word_id = hw.id
                            join r_words rw on rw.id = erw.r_word_id
                            join e_words ew on ew.id = erw.e_word_id
                            full outer join user_words uw on uw.custom_word_id = erw.id
                            join user_answers ua on erw.e_word_id = ua.id
                            where (uw.user_id = %s or uw.user_id is null)
                            and erw.id not in (select word_id from user_answers where answer = true order by random() limit 200)
                            ORDER BY random()/power(hw.id , 0.05) DESC
                            LIMIT 1;
                        """, (user_id,))
                    return cur.fetchone()
                except Exception as ex:
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print(message)

    def random_hebrew_words(self, word_to_avoid, user_id):

        output = []
        with psycopg2.connect(database=self.database, user=self.login, password=self.password) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                    select hw.word, hw.transcription
                        from he_words hw
                        join e_r_words erw on erw.e_word_id = hw.id 
                        full outer join user_words uw on uw.custom_word_id = erw.id 
                        where hw.word != %s and (uw.user_id = %s or uw.user_id is null)
                        ORDER BY random() LIMIT 4;
                    """, (word_to_avoid, user_id))
                    for row in cur.fetchall():
                        output.append([row[0], row[1]])
                    return output
                except Exception as ex:
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print(message)


    def random_rus_words(self, word_to_avoid, user_id):

        output = []
        with psycopg2.connect(database=self.database, user=self.login, password=self.password) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                    select rw.word
                        from r_words rw
                        join e_r_words erw on erw.r_word_id = rw.id 
                        full outer join user_words uw on uw.custom_word_id = erw.id 
                        where rw.word != %s and (uw.user_id = %s or uw.user_id is null)
                        ORDER BY random() LIMIT 4;
                    """, (word_to_avoid, user_id))
                    for row in cur.fetchall():
                        output.append(row[0])
                    return output
                except Exception as ex:
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print(message)


    def if_user_not_exist(self, user_id: int) -> bool:

        with psycopg2.connect(database=self.database, user=self.login, password=self.password) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                                select from users
                                where user_id = %s
                                """, (user_id,))
                    if cur.fetchone() is None:
                        return True
                except Exception as ex:
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print(message)


    def add_user(self, user_id, user_name):

        with psycopg2.connect(database=self.database, user=self.login, password=self.password) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                                insert into users (user_id, user_name)
                                values (%s, %s)
                                """, (user_id, user_name))
                    conn.commit()
                except Exception as ex:
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print(message)


    def add_word_to_dict(self, uid, word_e, word_r):

        with psycopg2.connect(database=self.database, user=self.login, password=self.password) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                                insert into e_words (word)
                                values (%s) RETURNING id
                                """, (word_e,))
                    e_word_id = cur.fetchone()[0]
                    cur.execute("""
                        insert into r_words (word)
                                values (%s) RETURNING id
                                """, (word_r,))
                    r_word_id = cur.fetchone()[0]
                    cur.execute("""
                        insert into e_r_words (e_word_id, r_word_id)
                        values (%s, %s) RETURNING id
                        """, (e_word_id, r_word_id))
                    e_r_word_id = cur.fetchone()[0]
                    cur.execute("""
                        insert into user_words (user_id, custom_word_id)
                        values (%s, %s)
                        """, (uid, e_r_word_id))
                    conn.commit()
                except Exception as ex:
                    if ex.pgcode == '23505':
                        return 'Duplicate'
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print(message)


    def delete_word_from_dict(self, uid, word_e):
        try:
            e_word_id = PostgreSQL.if_e_word_exists(self, uid, word_e)
            r_word_id = PostgreSQL.if_r_word_exists(self, uid, word_e)
            if e_word_id is not None:
                word_ids = PostgreSQL.find_e_word_links(self, e_word_id[0])
                r_word_id = word_ids[1]
                e_r_word_id = word_ids[0]
                PostgreSQL.delete_specific_word(self, e_r_word_id, e_word_id[0], r_word_id)
                return True
            elif r_word_id is not None and e_word_id is None:
                word_ids = PostgreSQL.find_r_word_links(self, r_word_id[0])
                e_word_id = word_ids[1]
                e_r_word_id = word_ids[0]
                PostgreSQL.delete_specific_word(self, e_r_word_id, e_word_id, r_word_id[0])
                return True
            else:
                return False
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)

    def delete_specific_word(self, e_r_word_id, e_word_id, r_word_id):

        with psycopg2.connect(database=self.database, user=self.login, password=self.password) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                        delete from user_words
                        where custom_word_id = %s
                        """, (e_r_word_id,))
                    cur.execute("""
                        delete from e_r_words
                        where id = %s
                        """, (e_r_word_id,))
                    cur.execute("""
                        delete from e_words
                        where id = %s
                        """, (e_word_id,))
                    cur.execute("""
                        delete from r_words
                        where id = %s
                        """, (r_word_id,))
                    conn.commit()
                except Exception as ex:
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print(message)


    def if_e_word_exists(self, uid, word):

        with psycopg2.connect(database=self.database, user=self.login, password=self.password) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                        select ew.id
                        from e_words ew 
                        join e_r_words erw on ew.id = erw.e_word_id 
                        join user_words uw on uw.custom_word_id = erw.id 
                        where uw.user_id = %s and ew.word = %s
                            """, (uid, word))
                    return cur.fetchone()
                except Exception as ex:
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print(message)


    def if_r_word_exists(self, uid, word):

        with psycopg2.connect(database=self.database, user=self.login, password=self.password) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                        select rw.id
                        from r_words rw 
                        join e_r_words erw on rw.id = erw.r_word_id 
                        join user_words uw on uw.custom_word_id = erw.id 
                        where uw.user_id = %s and rw.word = %s
                            """, (uid, word))
                    return cur.fetchone()
                except Exception as ex:
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print(message)


    def find_e_word_links(self, e_word_id):

        with psycopg2.connect(database=self.database, user=self.login, password=self.password) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                        select id, r_word_id from e_r_words
                        where e_word_id = %s
                        """, (e_word_id,))
                    return cur.fetchone()
                except Exception as ex:
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print(message)

    def find_r_word_links(self, r_word_id):

        with psycopg2.connect(database=self.database, user=self.login, password=self.password) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                        select id, e_word_id from e_r_words
                        where r_word_id = %s
                        """, (r_word_id,))
                    return cur.fetchone()
                except Exception as ex:
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print(message)

    def custom_words_user_count(self, uid):

        with psycopg2.connect(database=self.database, user=self.login, password=self.password) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                        select count(*) from user_words
                        where user_id = %s
                        """, (uid,))
                    return str(cur.fetchone()[0])
                except Exception as ex:
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print(message)

    def insert_user_answer(self, uid: int, word_id: int, answer: bool):
        with psycopg2.connect(database=self.database, user=self.login, password=self.password) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                        insert into user_answers
                        (user_id, word_id, answer)
                        values
                        (%s, %s, %s)
                        """, (uid, word_id, answer))
                    conn.commit()
                except Exception as ex:
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print(message)
    def show_user_statistics(self, uid: int) -> str:
        output = []
        with psycopg2.connect(database=self.database, user=self.login, password=self.password) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                        select count(ua.id )
                            from user_answers ua 
                            where ua.user_id = %s and answer = true
                            union all 
                            select count(ua.id )
                            from user_answers ua 
                            where ua.user_id = %s and answer = false 
                        """, (uid, uid))
                    for row in cur.fetchall():
                        output.append(str(row[0]))
                    ret = f'Made {int(output[0]) + int(output[1])} tries, {output[0]} correct answers and {output[1]} wrong answers. 🔥 Keep going! 🚀'
                    return ret
                except Exception as ex:
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print(message)