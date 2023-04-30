# -*- coding: utf-8 -*-

import telebot
from telebot import types
import random
from data.config import TOKEN
from data.models import User, Note, Session, Economic, Inco, Calc
import pywhatkit as kit
import os
import wikipedia
import soundfile as sf
import speech_recognition as sr
import requests
import datetime
import time
wikipedia.set_lang("ru")



bot = telebot.TeleBot(TOKEN)
toggle = 1
logfile = str(datetime.date.today()) + '.log'
value = '0'
old_value = '0'

keyboardd = telebot.types.InlineKeyboardMarkup()
keyboardd.row(telebot.types.InlineKeyboardButton(' ', callback_data='no'),
             telebot.types.InlineKeyboardButton('C', callback_data='C'),
             telebot.types.InlineKeyboardButton('<=', callback_data='<='),
             telebot.types.InlineKeyboardButton('/', callback_data='/'))
keyboardd.row(telebot.types.InlineKeyboardButton('7', callback_data='7'),
             telebot.types.InlineKeyboardButton('8', callback_data='8'),
             telebot.types.InlineKeyboardButton('9', callback_data='9'),
             telebot.types.InlineKeyboardButton('*', callback_data='*'))
keyboardd.row(telebot.types.InlineKeyboardButton('4', callback_data='4'),
             telebot.types.InlineKeyboardButton('5', callback_data='5'),
             telebot.types.InlineKeyboardButton('6', callback_data='6'),
             telebot.types.InlineKeyboardButton('-', callback_data='-'))
keyboardd.row(telebot.types.InlineKeyboardButton('1', callback_data='1'),
             telebot.types.InlineKeyboardButton('2', callback_data='2'),
             telebot.types.InlineKeyboardButton('3', callback_data='3'),
             telebot.types.InlineKeyboardButton('+', callback_data='+'))
keyboardd.row(telebot.types.InlineKeyboardButton(' ', callback_data='no'),
             telebot.types.InlineKeyboardButton('0', callback_data='0'),
             telebot.types.InlineKeyboardButton(',', callback_data=','),
             telebot.types.InlineKeyboardButton('=', callback_data='='))


def audio_to_text(dest_name: str):
    r = sr.Recognizer()
    message = sr.AudioFile(dest_name)
    with message as source:
        audio = r.record(source)
    result = r.recognize_google(audio, language="ru_RU")
    return result


@bot.message_handler(content_types=['voice'])
def get_audio_messages(message):
    try:
        print("Started recognition...")
        file_info = bot.get_file(message.voice.file_id)
        doc = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path))
        with open('voice.ogg', 'wb') as f:
            f.write(doc.content)
        data, samplerate = sf.read('voice.ogg')
        sf.write('new_file.wav', data, samplerate)
        result = audio_to_text('new_file.wav')
        bot.reply_to(message, result)
    except sr.UnknownValueError as e:
        bot.send_message(message.from_user.id,  "Прошу прощения, но я не разобрал сообщение, или оно поустое...")


@bot.message_handler(commands=['start'])
def start_handler(message):
    with Session() as session:
        user = session.query(User).filter_by(chat_id=message.chat.id).first()
        if user is None:
            user = User(chat_id=message.chat.id, username=message.chat.username)
            session.add(user)
            session.commit()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('🗓Заметки')
    button2 = types.KeyboardButton('📊Кошелек')
    button3 = types.KeyboardButton('🧸Безделушки')
    button4 = types.KeyboardButton('🖼Изображения')
    webAppTest = types.WebAppInfo("https://nilandvi.github.io/NandGbotWEB/") #создаем webappinfo - формат хранения url
    one_butt = types.KeyboardButton(text="ℹ️Помощь", web_app=webAppTest) #создаем кнопку типа webapp
    keyboard.add(button1, button2, button3, button4, one_butt)
    bot.reply_to(message, f"👋Добро пожаловать, {user.username}!\nВы успешно зарегистрировались✅\nТелеграм бот на питоне. Вид сбоку.\nХолст. Масло. 🖼",  reply_markup=keyboard)

@bot.message_handler(commands=['roulet'])
def handle_roulette(message):
    msg = bot.send_message(message.chat.id, "Достали револьвер")
    time.sleep(3)
    count_puncts = 0
    for i in range(9):
        if count_puncts <= 3:
            bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text="Крутим барабан" + '.' * count_puncts)
            count_puncts += 1
        else:
            count_puncts = 0
        time.sleep(0.5)
    bullet_location = random.randint(1, 4)
    user_choice = random.randint(1, 4)
    if user_choice == bullet_location:
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text="Вы проиграли :(")
    else:
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text="Вы победили!")

@bot.message_handler(commands=['new_note'])
def new_note_handler(message):
    session = Session()
    user = session.query(User).filter_by(chat_id=message.chat.id).first()
    if not user:
        bot.reply_to(message, "🔐Вы еще не зарегистрировались в боте!")
        return
    
    # Получаем текст новой заметки от пользователя
    bot.reply_to(message, "📝Введите текст заметки:")
    bot.register_next_step_handler(message, create_new_note, user.id)


def create_new_note(message, user_id):
    session = Session()
    if isinstance(message, telebot.types.Message):
        note = Note(user_id=str(user_id), note_text=message.text)
        session.add(note)
        session.commit()
        bot.send_message(chat_id=message.chat.id, text='✅Заметка добавлена')
    else:
        print(f'Invalid message type: {type(message)}')

@bot.message_handler(commands=['show_notes'])
def show_notes_handler(message):
    # Получаем текущего пользователя
    user = Session().query(User).filter_by(chat_id=message.chat.id).first()
    if not user:
        bot.reply_to(message, "🔐Вы еще не зарегистрировались в боте!")
        return

    # Получаем все заметки текущего пользователя
    notes = Session().query(Note).filter_by(user_id=user.id).all()
    if not notes:
        bot.reply_to(message, "📛У вас еще нет заметок.")
    else:
        bot.reply_to(message, "🗓Ваши заметки:")
        for note in notes:
            bot.send_message(message.chat.id, f"📝 {note.note_text}")

@bot.message_handler(commands=['delete_note'])
def delete_note_handler(message):
    session = Session()
    user = session.query(User).filter_by(chat_id=message.chat.id).first()
    if not user:
        bot.reply_to(message, "🔐Вы еще не зарегистрировались в боте!")
        return

    # Получаем все заметки текущего пользователя
    notes = session.query(Note).filter_by(user_id=user.id).all()
    if not notes:
        bot.reply_to(message, "📛У вас еще нет заметок.")
        return

    # Просим пользователя выбрать заметку, которую нужно удалить
    note_text = "\n".join([f"{i + 1}. {note.note_text}" for i, note in enumerate(notes)])
    bot.reply_to(message, f"🔢Выберите номер заметки, которую нужно удалить:\n{note_text}")
    bot.register_next_step_handler(message, remove_note, user.id)


def remove_note(message, user_id):
    session = Session()
    if not message.text.isdigit():
        bot.reply_to(message, "📛Номер заметки должен быть целым числом. Попробуйте еще раз:")
        bot.register_next_step_handler(message, remove_note, user_id)
        return

    # Получаем все заметки текущего пользователя
    notes = session.query(Note).filter_by(user_id=user_id).all()
    if not notes:
        bot.reply_to(message, "📛У вас еще нет заметок.")
        return

    note_number = int(message.text)
    if note_number < 1 or note_number > len(notes):
        bot.reply_to(message, "📛Некорректный номер заметки. Попробуйте еще раз:")
        bot.register_next_step_handler(message, remove_note, user_id)
        return

    # Удаляем выбранную заметку
    note_to_delete = notes[note_number - 1]
    session.delete(note_to_delete)
    session.commit()
    bot.reply_to(message, "✅Заметка успешно удалена!")


@bot.message_handler(commands=['expenses'])
def expens(message):
    session = Session()
    user = session.query(User).filter_by(chat_id=message.chat.id).first()
    if not user:
        bot.reply_to(message, "🔐Вы еще не зарегистрировались в боте!")
        return
    bot.reply_to(message, '❇️Введите расходы целым числом:')
    bot.register_next_step_handler(message, expen, user.id)


def expen(message, user_id):
    session = Session()
    if not message.text.isdigit():
        bot.reply_to(message, "📛расходы должны быть записаны целым числом. Попробуйте еще раз:")
        bot.register_next_step_handler(message, expen, user_id)
        return
    exc = int(message.text)
    if exc < 0:
        bot.reply_to(message, "📛Расходы не могут быть отрицательными")
        bot.register_next_step_handler(message, expen, user_id)
        return
    e = Economic(user_id=str(user_id), expenss=message.text)
    session.add(e)
    session.commit()
    bot.reply_to(message, '✅Запись о расходах успешно добавлена!')


@bot.message_handler(commands=['incomes'])
def incoms(message):
    session = Session()
    user = session.query(User).filter_by(chat_id=message.chat.id).first()
    if not user:
        bot.reply_to(message, "🔐Вы еще не зарегистрировались в боте!")
        return
    bot.reply_to(message, '❇️Введите доходы целым числом:')
    bot.register_next_step_handler(message, incom, user.id)


def incom(message, user_id):
    session = Session()
    if not message.text.isdigit():
        bot.reply_to(message, "📛доходы должны быть записаны целым числом. Попробуйте еще раз:")
        bot.register_next_step_handler(message, incom, user_id)
        return
    exc = int(message.text)
    if exc < 0:
        bot.reply_to(message, "📛Доходы не могут быть отрицательными")
        bot.register_next_step_handler(message, incom, user_id)
        return
    e = Inco(user_id=str(user_id), incom=message.text)
    session.add(e)
    session.commit()
    bot.reply_to(message, '✅Запись о доходах успешно добавлена!')


@bot.message_handler(commands=['show_expenses'])
def show_exp_handler(message):
    # Получаем текущего пользователя
    user = Session().query(User).filter_by(chat_id=message.chat.id).first()
    if not user:
        bot.reply_to(message, "🔐Вы еще не зарегистрировались в боте!")
        return

    # Получаем все заметки текущего пользователя
    notes = Session().query(Economic).filter_by(user_id=user.id).all()
    if not notes:
        bot.reply_to(message, "📛У вас еще нет записанных расходов.")
    else:
        bot.reply_to(message, "✅Ваши расходы:")
        for note in notes:
            bot.send_message(message.chat.id, f"➖ {note.expenss} рублей")


@bot.message_handler(commands=['show_incomes'])
def show_inc_handler(message):
    # Получаем текущего пользователя
    user = Session().query(User).filter_by(chat_id=message.chat.id).first()
    if not user:
        bot.reply_to(message, "🔐Вы еще не зарегистрировались в боте!")
        return

    # Получаем все заметки текущего пользователя
    notes = Session().query(Inco).filter_by(user_id=user.id).all()
    if not notes:
        bot.reply_to(message, "📛У вас еще нет записанных доходов.")
    else:
        bot.reply_to(message, "✅Ваши доходы:")
        for note in notes:
            bot.send_message(message.chat.id, f"➕ {note.incom} рублей")

if not os.path.exists('asciiart'):
    os.makedirs('asciiart')

@bot.message_handler(commands=["static"])
def econom_static(message):
    user = Session().query(User).filter_by(chat_id=message.chat.id).first()
    if not user:
        bot.reply_to(message, "🔐Вы еще не зарегистрировались в боте!")
        return

    notes = Session().query(Inco).filter_by(user_id=user.id).all()
    notesexp = Session().query(Economic).filter_by(user_id=user.id).all()
    if not notes and not notesexp:
        bot.reply_to(message, "📛У вас еще нет записанных доходов и расходов. Статистика невозможна.")
    else:
        summ = 0
        ub = 0
        for note in notes:
            summ += int(note.incom)
        for exp in notesexp:
            ub += int(exp.expenss)
        total = summ - ub
        if total < 0: 
            bot.send_message(message.chat.id, "Знаете, если ваши расходы превышают доходы, у налоговой будет много вопросов к вам, но я не в праве Вам мешать:")
        bot.reply_to(message, f"👛Ваш кошелек:\n💠Общая сумма: {total}\n➖Затрат за все время: {ub}\n➕Прибыль за все время: {summ}\n")


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    global toggle
    if toggle == 1:
        photo = message.photo[-1]
        file_info = bot.get_file(photo.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('asciiart/image.jpg', 'wb') as new_file:
            new_file.write(downloaded_file)
        ascii_art = kit.image_to_ascii_art('asciiart/image.jpg', "Твоя картинка")
        with open('asciiart/Твоя картинка.txt', 'w') as file:
            file.write(ascii_art)
        with open('asciiart/Твоя картинка.txt', 'rb') as file:
            bot.send_document(message.chat.id, file)
            toggle = 0
    elif toggle == 0:
        bot.send_message(message.chat.id, f"Я не знаю что делать с твоей фотографией")


@bot.message_handler(commands=['calculator'])
def calc(message):
    global value
    user = Session().query(User).filter_by(chat_id=message.chat.id).first()
    if not user:
        bot.reply_to(message, "🔐Вы еще не зарегистрировались в боте!")
        return
    bot.send_message(message.chat.id, '0', reply_markup=keyboardd)
    if value == '0':
        bot.send_message(message.from_user.id, '0', reply_markup=keyboardd)
    else:
        bot.send_message(message.from_user.id, value, reply_markup=keyboardd)
@bot.callback_query_handler(func=lambda call: True)
def calback(query):
    global value, old_value
    user = Session().query(User).filter_by(chat_id=query.message.chat.id).first()
    if not user:
        bot.send_message(query.message.from_user.id, "🔐Вы еще не зарегистрировались в боте!")
        return

    data = query.data
    if data == 'no':
        pass
    elif data == 'C':
        value = '0'
    elif data == '<=':
        if value != '0':
            value = value[:len(value)-1]
    elif data == '=':
        try:
            value = str(eval(value[1::]))
        except:
            value = 'ошибка'
    else:
        value += data
    if (value != old_value and value != '0') or ('0' != old_value and value == '0'):
        if value == '0':
            bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text='0',
                                  reply_markup=keyboardd)
            old_value = '0'
        else:
            bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text=value,
                                  reply_markup=keyboardd)
            old_value = value
    if value == 'ошибка':
        value = '0'
@bot.message_handler(content_types=['text'])
def bot_message(message):
    session = Session()
    user = session.query(User).filter_by(chat_id=message.chat.id).first()
    if message.chat.type == "private":
        if message.text == "📊Кошелек":
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button1 = types.KeyboardButton('/expenses')
            button2 = types.KeyboardButton('/show_expenses')
            button3 = types.KeyboardButton('/incomes')
            button4 = types.KeyboardButton('/show_incomes')
            button5 = types.KeyboardButton("/static")
            bt = types.KeyboardButton('⬅️Назад')
            keyboard.add(button1, button2, button3, button4, button5, bt)
            bot.reply_to(message, f"🧮Добро пожаловать в раздел управления финансами!\n/expenses - Добавить расходы\n/show_expenses - История расходов\n/incomes - Добавить зачисления\n/show_incomes - История зачислений\n/static - Личный кошелек\n", reply_markup=keyboard)
        elif message.text == "🗓Заметки":
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button1 = types.KeyboardButton('/new_note')
            button2 = types.KeyboardButton('/show_notes')
            button3 = types.KeyboardButton('/delete_note')
            bt = types.KeyboardButton('⬅️Назад')
            keyboard.add(button1, button2, button3, bt)
            bot.reply_to(message, f"📚Добро пожаловать в раздел заметок!\n/new_note - создать новую заметку\n/show_notes - посмотреть свои заметки\n/delete_note - удалить заметку\n", reply_markup=keyboard)
        elif message.text == "⬅️Назад":
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                button1 = types.KeyboardButton('🗓Заметки')
                button2 = types.KeyboardButton('📊Кошелек')
                button3 = types.KeyboardButton('🧸Безделушки')
                button4 = types.KeyboardButton('🖼Изображения')
                webAppTest = types.WebAppInfo("https://nilandvi.github.io/NandGbotWEB/") #создаем webappinfo - формат хранения url
                one_butt = types.KeyboardButton(text="ℹ️Помощь", web_app=webAppTest) #создаем кнопку типа webapp
                keyboard.add(button1, button2, button3, button4, one_butt)
                bot.send_message(message.chat.id, f"Привет, {user.username}\n✅Ты в главном меню",  reply_markup=keyboard)
        elif message.text == 'отсоси мне':
            bot.send_message(message.chat.id, 'Дурка выехала....')
        elif message.text == '🧸Безделушки':
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button1 = types.KeyboardButton('/roulet')
            button2 = types.KeyboardButton('/calculator')
            bt = types.KeyboardButton('⬅️Назад')
            bt2 = types.KeyboardButton('Генератор')
            keyboard.add(button1, button2, bt, bt2)
            bot.send_message(message.chat.id, "Добро пожаловать в раздел безделушек. Единтсвенное что тут етсь это баганный калькулятор, но сегодня днем будет не только калькулятор!", reply_markup=keyboard)
        elif message.text == '🖼Изображения':
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            bt = types.KeyboardButton('⬅️Назад')
            keyboard.add(bt)
            bot.send_message(message.chat.id, "Раздел в режиме разработки", reply_markup=keyboard)
        elif message.text == '2' or message.text == '10' or message.text == '20' or message.text == '50' or message.text == '100' or message.text == '1000':
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            bt = types.KeyboardButton('⬅️Назад')
            keyboard.add(bt)
            bot.send_message(message.chat.id, str(random.randint(1, int(message.text))), reply_markup=keyboard)
        elif message.text == 'Генератор':
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button1 = types.KeyboardButton('2')
            button2 = types.KeyboardButton('10')
            bt = types.KeyboardButton('20')
            button3 = types.KeyboardButton('50')
            button4 = types.KeyboardButton('100')
            bt2 = types.KeyboardButton('1000')
            keyboard.add(button1)
            keyboard.add(button2)
            keyboard.add(bt)
            keyboard.add(button3)
            keyboard.add(button4)
            keyboard.add(bt2)
            bot.send_message(message.chat.id, 'Введите число, до которого нужно сгенерировать рандомное число:', reply_markup=keyboard)

        else:
            word = message.text.strip().lower()
            try:
                # search for articles related to the input query
                results = wikipedia.search(word, results=1)
                if results:
                    # get the summary of the first article from the search results
                    final_message = wikipedia.summary(results[0])
                else:
                    final_message = "Ой, ты слишком умный для википедии. Я ничего не нашел"
            except wikipedia.exceptions.DisambiguationError as e:
                # handle disambiguation error by printing the list of options
                final_message = f"Ой, я ничего не смог найти по запросу '{e.title}'. Попробуй переформулировать вопрос или следующие варианты:\n\n"
                final_message += "\n".join(e.options)
            except wikipedia.exceptions.PageError:
                final_message = "Ой, ты слишком умный для википедии. Я ничего не нашел"
            bot.send_message(message.chat.id, final_message, parse_mode="HTML")


bot.polling(none_stop=True, interval=0)
