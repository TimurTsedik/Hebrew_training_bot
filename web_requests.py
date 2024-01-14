from typing import List, Any

import requests
from bs4 import BeautifulSoup
import psycopg2
import deepl


def contains_latin_alphabet(input_string):
    return any(char.isascii() and char.isalpha() for char in input_string)


def get_words_from_web_page():
    url = 'https://www.teachmehebrew.com/hebrew-frequency-list.html'
    response = requests.get(url)
    page_text = response.text
    #parsing webpage text

    return response


def get_words_from_web_page():
    url = 'https://www.teachmehebrew.com/hebrew-frequency-list.html'
    response = requests.get(url)
    page_text = response.text
    with psycopg2.connect(database="telegram_hebrew", user="postgres", password="postgres") as conn:
        with conn.cursor() as cur:
    # Parsing webpage text
            soup = BeautifulSoup(page_text, 'html.parser')
            counter= 0
            for tag in soup.find_all('td'):
                tag_text = tag.text.strip()
                if not '\n' in tag_text and len(tag_text) > 0:
                    clear_string = tag_text.replace('\t', '')
                    if clear_string.isnumeric():
                        counter = 1
                        article_nr: int = int(clear_string)
                    elif contains_latin_alphabet(clear_string):
                        if counter == 2:
                            transcription = clear_string
                            counter = 3
                        elif counter == 1:
                            counter = 2
                            e_word = clear_string
                    elif not contains_latin_alphabet(clear_string):
                        counter = 4
                        he_word = clear_string
                        if counter == 4:
                            cur.execute("""
                                INSERT INTO e_words (id, word)
                                VALUES (%s, %s)
                            """, (article_nr, e_word))
                            cur.execute("""
                                INSERT INTO he_words (id, word, transcription)
                                VALUES (%s, %s, %s)
                            """, (article_nr, he_word, transcription))
                            cur.execute("""
                                INSERT INTO e_r_words (e_word_id, he_word_id, r_word_id)
                                VALUES (%s, %s, %s)
                                """, (article_nr, article_nr, 0))
                            print(article_nr)

            conn.commit()
                    
# def yandex_translate_word(word):
#     url = 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup'
#     token = 'dict.1.1.20240105T110743Z.600ac8480e33f6f1.2f8ae94a593c6a3e9eafcb66bdf71633ec1069ec'
#     final_url = url + '?key=' + token + '&lang=en-ru&text=' + word
#     resp = requests.get(final_url)
#     translation = resp.json()
#     print(final_url)
#     trans_word = translation['def'][0]['tr'][0]['text']
#     return trans_word

def deepl_translate_word(word):
    auth_key = "2aa2a80c-6139-4c34-814b-3f0424b7abb4:fx"  # Replace with your key
    translator = deepl.Translator(auth_key)

    result = str(translator.translate_text(word, target_lang="RU"))
    return result


def get_russian_translate():
    with psycopg2.connect(database="telegram_hebrew", user="postgres", password="postgres") as conn:
        with conn.cursor() as cur:
            i = 3581
            try:
                for i_ in range(i, 10001):
                    output = []
                    cur.execute("""
                    SELECT word FROM e_words WHERE id = %s
                    """, (i_,))
                    e_word = cur.fetchone()[0]
                    wordlist = get_from_dict_string(e_word)
                    for word in wordlist:
                        if word != '':
                            output.append(deepl_translate_word(word))
                    output_text = ', '.join(output)
                    cur.execute("""
                    insert into r_words (id, word)
                    values (%s, %s)
                    """, (i_, output_text))

                    print(i_)
                    if i_ % 20 == 0:
                        conn.commit()
                conn.commit()
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print(message)


def get_from_dict_string(wordlist: list) -> list:
    str_list = wordlist.split(' / ')
    output_list: list[Any] = []
    for str in str_list:
        if '(' in str:
            output_list.append(str[0:str.find('(')-1].strip())
        else:
            output_list.append(str.strip())
    return output_list


# print(get_words_from_web_page())
# get_words_from_web_page()
# print(contains_latin_alphabet('קרארק'))

# print(deepl_translate_word("became established"))
# print(get_russian_translate("that/who were introduced / that were displayed / that were presented / that were exhibited (pl.)"))
# print(get_from_dict_string('of / belongs to'))
print(get_russian_translate())
# print(get_from_dict_string("that/who stood / that/who was about to / that/who endured / that/who succeeded / that/who insisted on (m.s.)"))
