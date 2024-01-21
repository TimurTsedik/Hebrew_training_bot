import random

from telebot import types, TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup

from dict_jobs import PostgreSQL
from credentials import token_bot

print('Start telegram bot...')

state_storage = StateMemoryStorage()
bot = TeleBot(token_bot, state_storage=state_storage)

known_users = []
userStep = {}
buttons = []
e_word_to_add = {}
r_word_to_add = {}
rus_hebrew = False
en_hebrew = True
postgresql = PostgreSQL()
current_word_id = {}

def show_hint(*lines):
    return '\n'.join(lines)


def show_target(data):
    return f"{data['target_word']} -> {data['translate_word']}"


class Command:
    if en_hebrew:
        MISTAKES = 'My mistakes'
        STATS = 'Statistics'
        NEXT = 'Next ⏭'
    else:
        MISTAKES = 'Мои ошибки'
        NEW_WORDS = 'Статистика'
        STATS = 'Дальше ⏭'


class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()


def get_user_step(uid):
    if PostgreSQL.if_user_not_exist(postgresql, uid):
        known_users.append(uid)
        userStep[uid] = 0
        print("New user detected, who hasn't used \"/start\" yet")
        return 0
    else:
        return userStep[uid]


@bot.message_handler(commands=['cards', 'start'])
def create_cards(message):

    cid = message.chat.id
    user_name = message.from_user.first_name
    if PostgreSQL.if_user_not_exist(postgresql, cid):
        known_users.append(cid)
        PostgreSQL.add_user(postgresql, cid, message.from_user.first_name)
        bot.send_message(cid, f"Welcome, {user_name}, let's learn עבר׳ת?")

    markup = types.ReplyKeyboardMarkup(row_width=2)

    global buttons
    buttons = []
    if cid not in userStep:
        userStep[cid] = 0
    mistakes = userStep[cid] == 5
    words = PostgreSQL.random_word_from_base(postgresql, cid, mistakes)
    transcription = words[2]
    current_word_id[cid] = words[4]
    if en_hebrew:
        target_word = words[0]
        translate = words[3]
        others = list(PostgreSQL.random_hebrew_words(postgresql, target_word, cid))
    if rus_hebrew:
        target_word = words[0]
        translate = words[1]
        others = list(PostgreSQL.random_hebrew_words(postgresql, target_word, cid))
    # else:
    #     target_word = words[1]
    #     translate = words[0]
    #     others = list(random_rus_words(target_word, cid))
    target_word_btn = types.KeyboardButton(target_word + ' (' + transcription + ')')
    buttons.append(target_word_btn)
    if en_hebrew:
        words_trans = []
        for word in others:
            words_trans.append(word[0] + ' (' + word[1] + ')')
        other_words_btns = [types.KeyboardButton(word) for word in words_trans]

    if rus_hebrew:
        words_trans = []
        for word in others:
            words_trans.append(word[0] + ' (' + word[1] + ')')
        other_words_btns = [types.KeyboardButton(word) for word in words_trans]
    # else:
    #     other_words_btns = [types.KeyboardButton(word) for word in others]
    buttons.extend(other_words_btns)
    random.shuffle(buttons)
    next_btn = types.KeyboardButton(Command.NEXT)
    # add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    # delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    mistakes_btn = types.KeyboardButton(Command.MISTAKES)
    statistics_btn = types.KeyboardButton(Command.STATS)
    buttons.extend([next_btn, mistakes_btn, statistics_btn])

    markup.add(*buttons)
    if en_hebrew:
        greeting = f"Select correct translation:\n {translate}"
    else:
        greeting = f"Выбери перевод слова:\n {translate}"
    bot.send_message(message.chat.id, greeting, reply_markup=markup)
    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = target_word
        data['translate_word'] = translate
        data['other_words'] = others


@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    create_cards(message)


@bot.message_handler(func=lambda message: message.text == Command.MISTAKES)
def mistakes_work(message):
    uid = message.from_user.id
    if uid not in userStep or userStep[uid] != 5:
        Command.MISTAKES = "Return to base study"
        userStep[uid] = 5
    else:
        Command.MISTAKES = "My mistakes"
        userStep[uid] = 0
    create_cards(message)


@bot.message_handler(func=lambda message: message.text == Command.STATS)
def show_stats(message):
    uid = message.from_user.id
    hint = PostgreSQL.show_user_statistics(postgresql, uid)
    markup = types.ReplyKeyboardMarkup(row_width=2)
    bot.send_message(message.chat.id, hint, reply_markup=markup)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    sucsess = False
    text = message.text
    print('request from user: ', message.from_user.first_name)
    markup = types.ReplyKeyboardMarkup(row_width=2)
    if len(userStep) == 0 or userStep.get(message.from_user.id) == 0 or userStep.get(message.from_user.id) == 5:
        if len(userStep) == 0:
            userStep[message.from_user.id] = 0
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            target_word = data['target_word']
            answer = text.split(' (')[0] == target_word
            PostgreSQL.insert_user_answer(postgresql, message.from_user.id, current_word_id[message.from_user.id], answer)
            if answer:
                hint = show_target(data)
                if en_hebrew:
                    hint_text = ["Excellent!❤", hint]
                else:
                    hint_text = ["Отлично!❤", hint]
                hint = show_hint(*hint_text)
                sucsess = True
            else:
                for btn in buttons:
                    if btn.text == text:
                        btn.text = text + '❌'
                        break
                if en_hebrew:
                    hint = show_hint("Error!",
                                     f"Please try again {data['translate_word']}")
                else:
                    hint = show_hint("Допущена ошибка!",
                                 f"Попробуй ещё раз вспомнить слово {data['translate_word']}")
    elif userStep[message.from_user.id] == 1:
        e_word_to_add[message.from_user.id] = text
        hint = "Отлично, теперь введите значение слова " + text
        userStep[message.from_user.id] = 2
    elif userStep[message.from_user.id] == 2:
        r_word_to_add[message.from_user.id] = text
        userStep[message.from_user.id] = 0
        if PostgreSQL.add_word_to_dict(postgresql, message.from_user.id, e_word_to_add[message.from_user.id],
                            r_word_to_add[message.from_user.id]) == 'Duplicate':
            hint = "Такое слово уже есть в словаре"
        else:
            hint = "Отлично, запишем слово " + text + ". в словаре уже "
            hint += PostgreSQL.custom_words_user_count(postgresql, message.from_user.id) + " ваших слов"
        e_word_to_add.pop(message.from_user.id)
        r_word_to_add.pop(message.from_user.id)
    elif userStep[message.from_user.id] == 3:
        if not PostgreSQL.delete_word_from_dict(postgresql, message.from_user.id, text):
            hint = "Такого слова нет в словаре"
        else:
            hint = "Отлично, вы удалили слово " + text + ". в словаре уже "
            hint += PostgreSQL.custom_words_user_count(postgresql, message.from_user.id) + " ваших слов"
        userStep[message.from_user.id] = 0
    # markup.add(*buttons)
    bot.send_message(message.chat.id, hint, reply_markup=markup)
    if sucsess:
        next_cards(message)

bot.add_custom_filter(custom_filters.StateFilter(bot))

bot.infinity_polling(skip_pending=True)
