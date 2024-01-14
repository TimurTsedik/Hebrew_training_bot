import psycopg2


def random_word_from_base(user_id):
    """
    Function Purpose:

    This function is designed to retrieve a random word pair (one Russian word
    and its corresponding English word) from the database. The selection considers
    the specified user's associations with words.

    Parameters:

    user_id: The ID of the user for whom the word associations are considered.
    Return Value:

    A tuple containing the selected Russian word (r_w) and its corresponding English word (e_w).
    Database Query Explanation:

    Select Statement:
    Retrieves a pair of words, where rw.word represents the Russian word, and ew.word
    represents the corresponding English word.
    Joins the r_words table to establish associations with Russian words.
    Joins the e_r_words table to link Russian words with their corresponding English words.
    Joins the e_words table to get the actual English words.
    Uses a full outer join with the user_words table to include words that
    might not have associations with the given user.
    Applies conditions to consider the specified user (uw.user_id = %s or uw.user_id is null).
    Orders the results randomly (ORDER BY random()) and limits the result set to 1 word pair (LIMIT 1).
    Exception Handling:
    Catches any exceptions that might occur during the execution of the query.
    Prints detailed information about the exception for debugging purposes.
    """
    with psycopg2.connect(database="telegram_hebrew", user="postgres", password="postgres") as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("""
                SELECT hw.word as h_w, rw.word as r_w, hw.transcription as h_t, ew.word as e_w
                    from he_words hw
                    join e_r_words erw on erw.r_word_id = hw.id 
                    join r_words rw on rw.id = erw.r_word_id
                    join e_words ew on ew.id = erw.e_word_id
                    full outer join user_words uw on uw.custom_word_id = erw.id
                    where uw.user_id = %s or uw.user_id is null
                    ORDER BY random()/power(hw.id , 0.01) DESC
                    LIMIT 1;
                """, (user_id,))
                return cur.fetchone()
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print(message)

def random_hebrew_words(word_to_avoid, user_id):
    """
    Function Purpose:

    This function is designed to retrieve a list of random English words from the database,
    excluding a specific word and considering a specific user's associations.

    Parameters:

    word_to_avoid: The English word that should be excluded from the result.
    user_id: The ID of the user for whom the word associations are considered.
    Return Value:
    A list of English words (up to 4) that meet the specified criteria.
    Database Query Explanation:

    Select Statement:

    Retrieves English words (ew.word) from the e_words table.
    Joins the e_r_words table to establish associations with Russian words.
    Uses a full outer join with the user_words table to include words that might not
    have associations with the given user.
    Applies conditions to exclude a specific word (ew.word != %s) and consider
    the specified user ((uw.user_id = %s or uw.user_id is null)).
    Orders the results randomly (ORDER BY random()) and limits the result
    set to 4 words (LIMIT 4).
    Exception Handling:
    Catches any exceptions that might occur during the execution of the query.
    Prints detailed information about the exception for debugging purposes.
    """
    output = []
    with psycopg2.connect(database="telegram_hebrew", user="postgres", password="postgres") as conn:
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


def random_rus_words(word_to_avoid, user_id):
    """
    Function Purpose:

    This function is designed to retrieve a list of random Russian words
    from the database, excluding a specific word and considering a specific user's associations.

    Parameters:

    word_to_avoid: The Russian word that should be excluded from the result.
    user_id: The ID of the user for whom the word associations are considered.
    Return Value:

    A list of Russian words (up to 4) that meet the specified criteria.
    Database Query Explanation:

    Select Statement:
    Retrieves Russian words (rw.word) from the r_words table.
    Joins the e_r_words table to establish associations with English words.
    Uses a full outer join with the user_words table to include words that might
    not have associations with the given user.
    Applies conditions to exclude a specific word (rw.word != %s) and consider
    the specified user ((uw.user_id = %s or uw.user_id is null)).
    Orders the results randomly (ORDER BY random()) and limits the result
    set to 4 words (LIMIT 4).
    Exception Handling:
    Catches any exceptions that might occur during the execution of the query.
    Prints detailed information about the exception for debugging purposes.
    """
    output = []
    with psycopg2.connect(database="telegram_hebrew", user="postgres", password="postgres") as conn:
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


def if_user_not_exist(user_id):
    """
    Function Purpose:

    This function is designed to check whether a user with the given ID exists in the database.

    Parameters:

    user_id: The ID of the user to check for existence.
    Return Value:

    True if the user does not exist in the database, False otherwise.
    Database Query Explanation:

    Select Statement:
    Checks for the existence of a user in the users table based on the provided user_id.
    Retrieves a row from the users table where user_id matches the input.
    The function returns True if no matching user is found (result set is None),
    indicating that the user does not exist.
    Exception Handling:
    Catches any exceptions that might occur during the execution of the query.
    Prints detailed information about the exception for debugging purposes.
    """
    with psycopg2.connect(database="telegram_hebrew", user="postgres", password="postgres") as conn:
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


def add_user(user_id, user_name):
    """
    Function Purpose:

    This function is designed to add a new user to the database with the provided user ID and username.

    Parameters:

    user_id: The ID of the user to be added.
    user_name: The username of the user to be added.
    Return Value:

    None (no explicit return value).
    Database Query Explanation:

    Insert Statement:
    Inserts a new row into the users table with the specified user_id and user_name.
    Commit:
    Commits the transaction to persist the changes in the database.
    Exception Handling:
    Catches any exceptions that might occur during the execution of the query.
    Prints detailed information about the exception for debugging purposes.
    """
    with psycopg2.connect(database="telegram_hebrew", user="postgres", password="postgres") as conn:
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


def add_word_to_dict(uid, word_e, word_r):
    """
    Function Purpose:

    This function is designed to add a new custom word pair to the user's
    dictionary in the database. It includes the English word, Russian word, and their association.

    Parameters:

    uid: The ID of the user to whom the custom word pair is associated.
    word_e: The English word to be added.
    word_r: The corresponding Russian word to be added.
    Return Value:

    If the operation is successful, the function returns None.
    If there's an attempt to insert a duplicate entry, the function returns the string 'Duplicate'.
    Database Query Explanation:

    Insert Statements:
    Inserts the provided English word (word_e) into the e_words table, returning
    the generated ID (e_word_id).
    Inserts the provided Russian word (word_r) into the r_words table, returning
    the generated ID (r_word_id).
    Inserts a row into the e_r_words table, establishing the association between
    the English and Russian words, returning the generated ID (e_r_word_id).
    Inserts a row into the user_words table, associating the custom word with
    the specified user.
    Commit:
    Commits the transaction to persist the changes in the database.
    Duplicate Entry Handling:
    Checks if the exception has a PostgreSQL error code '23505', which indicates
    a violation of a unique constraint (duplicate entry). In such cases, the function returns 'Duplicate'.
    Exception Handling:
    Catches any exceptions that might occur during the execution of the queries.
    Prints detailed information about the exception for debugging purposes.
    """
    with psycopg2.connect(database="telegram_hebrew", user="postgres", password="postgres") as conn:
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


def delete_word_from_dict(uid, word_e):
    try:
        e_word_id = if_e_word_exists(uid, word_e)
        r_word_id = if_r_word_exists(uid, word_e)
        if e_word_id is not None:
            word_ids = find_e_word_links(e_word_id[0])
            r_word_id = word_ids[1]
            e_r_word_id = word_ids[0]
            delete_specific_word(e_r_word_id, e_word_id[0], r_word_id)
            return True
        elif r_word_id is not None and e_word_id is None:
            word_ids = find_r_word_links(r_word_id[0])
            e_word_id = word_ids[1]
            e_r_word_id = word_ids[0]
            delete_specific_word(e_r_word_id, e_word_id, r_word_id[0])
            return True
        else:
            return False
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)

def delete_specific_word(e_r_word_id, e_word_id, r_word_id):
    """
    Function Purpose:

    This function is designed to delete a custom word pair
    (English word and its associated Russian word) from the user's dictionary in the database.

    Parameters:

    uid: The ID of the user from whom the custom word pair is to be deleted.
    word_e: The English word for which the association is to be removed.
    Return Value:

    True if the deletion is successful.
    False if no matching custom word pair is found for deletion.
    Database Query Explanation:

    Check for Existing Words:
    Calls two helper functions (if_e_word_exists and if_r_word_exists) to check
    if the provided English word exists in the database.
    Determines the IDs of the English word (e_word_id) and the corresponding
    Russian word (r_word_id) if they exist.
    Delete Operation:
    If the English word exists (e_word_id is not None):
    Finds the IDs of the associated English-Russian word links (e_r_word_id).
    Calls the delete_specific_word function to delete the word associations from the database.
    If only the Russian word exists (r_word_id is not None):
    Finds the IDs of the associated Russian-English word links (e_r_word_id).
    Calls the delete_specific_word function to delete the word associations from the database.
    Exception Handling:
    Catches any exceptions that might occur during the execution of the queries.
    Prints detailed information about the exception for debugging purposes.
    """
    with psycopg2.connect(database="telegram_hebrew", user="postgres", password="postgres") as conn:
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


def if_e_word_exists(uid, word):
    """
    Function Purpose:

    This function is designed to check if a specific English word associated
     with a user exists in the database.

    Parameters:

    uid: The ID of the user for whom the association is checked.
    word: The English word to check for existence.
    Return Value:

    If the English word exists, the function returns the ID of the word (ew.id).
    If the word does not exist, the function returns None.
    Database Query Explanation:

    Select Statement:
    Retrieves the ID (ew.id) of the English word (e_words) associated with a user.
    Joins the e_r_words table to establish associations with Russian words.
    Joins the user_words table to get user-specific associations.
    Applies conditions to check if the provided user ID and English word
    match (uw.user_id = %s and ew.word = %s).
    Exception Handling:
    Catches any exceptions that might occur during the execution of the query.
    Prints detailed information about the exception for debugging purposes.
    """
    with psycopg2.connect(database="telegram_hebrew", user="postgres", password="postgres") as conn:
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


def if_r_word_exists(uid, word):
    """
    Function Purpose:

    This function is designed to check if a specific Russian word associated
    with a user exists in the database.

    Parameters:

    uid: The ID of the user for whom the association is checked.
    word: The Russian word to check for existence.
    Return Value:

    If the Russian word exists, the function returns the ID of the word (rw.id).
    If the word does not exist, the function returns None.
    Database Query Explanation:

    Select Statement:
    Retrieves the ID (rw.id) of the Russian word (r_words) associated with a user.
    Joins the e_r_words table to establish associations with English words.
    Joins the user_words table to get user-specific associations.
    Applies conditions to check if the provided user ID and Russian word match
    (uw.user_id = %s and rw.word = %s).
    Exception Handling:
    Catches any exceptions that might occur during the execution of the query.
    Prints detailed information about the exception for debugging purposes.
    """
    with psycopg2.connect(database="telegram_hebrew", user="postgres", password="postgres") as conn:
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


def find_e_word_links(e_word_id):
    """
    Function Purpose:

    This function is designed to find the links (IDs) between an English word
    and its associated Russian words in the e_r_words table.

    Parameters:

    e_word_id: The ID of the English word for which the links are to be found.
    Return Value:

    A tuple containing the ID of the English-Russian word link (e_r_word_id)
     and the ID of the associated Russian word (r_word_id).
    Database Query Explanation:

    Select Statement:
    Retrieves the ID of the English-Russian word link (e_r_word_id) and the
    ID of the associated Russian word (r_word_id).
    Filters the results based on the provided e_word_id to find the associations
    specific to that English word.
    Exception Handling:
    Catches any exceptions that might occur during the execution of the query.
    Prints detailed information about the exception for debugging purposes.
    """
    with psycopg2.connect(database="telegram_hebrew", user="postgres", password="postgres") as conn:
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

def find_r_word_links(r_word_id):
    """
    Function Purpose:

    This function is designed to find the links (IDs) between a Russian
    word and its associated English words in the e_r_words table.

    Parameters:

    r_word_id: The ID of the Russian word for which the links are to be found.
    Return Value:

    A tuple containing the ID of the English-Russian word link (e_r_word_id)
    and the ID of the associated English word (e_word_id).
    Database Query Explanation:

    Select Statement:
    Retrieves the ID of the English-Russian word link (e_r_word_id) and the ID
    of the associated English word (e_word_id).
    Filters the results based on the provided r_word_id to find the associations
    specific to that Russian word.
    Exception Handling:
    Catches any exceptions that might occur during the execution of the query.
    Prints detailed information about the exception for debugging purposes.
    """
    with psycopg2.connect(database="telegram_hebrew", user="postgres", password="postgres") as conn:
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

def custom_words_user_count(uid):
    """
    Function Purpose:

    This function is designed to retrieve the count of custom word pairs associated
    with a specific user in the user_words table.

    Parameters:

    uid: The ID of the user for whom the count is requested.
    Return Value:

    A string representation of the count of custom word pairs associated with the user.
    Database Query Explanation:

    Select Statement:
    Retrieves the count of rows in the user_words table where the user_id matches the provided uid.
    Exception Handling:
    Catches any exceptions that might occur during the execution of the query.
    Prints detailed information about the exception for debugging purposes.
    """
    with psycopg2.connect(database="telegram_hebrew", user="postgres", password="postgres") as conn:
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