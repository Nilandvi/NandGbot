import telebot
from telebot import types
import random
from data.config import TOKEN
from data.models import User, Note, Session, Economic, Inco
import pywhatkit as kit
import os
import wikipedia
wikipedia.set_lang("ru")


bot = telebot.TeleBot(TOKEN)
toggle = 1

def webAppKeyboard(): #создание клавиатуры с webapp кнопкой
   keyboard = types.ReplyKeyboardMarkup(row_width=1) #создаем клавиатуру
   webAppTest = types.WebAppInfo("https://telegram.mihailgok.ru") #создаем webappinfo - формат хранения url
   one_butt = types.KeyboardButton(text="Тестовая страница", web_app=webAppTest) #создаем кнопку типа webapp
   keyboard.add(one_butt) #добавляем кнопки в клавиатуру

   return keyboard #возвращаем клавиатуру


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
    button3 = types.KeyboardButton('👨‍💻Разработчики')
    webAppTest = types.WebAppInfo("https://telegram.mihailgok.ru") #создаем webappinfo - формат хранения url
    one_butt = types.KeyboardButton(text="Web🌐", web_app=webAppTest) #создаем кнопку типа webapp
    button4 = types.KeyboardButton('ℹ️Помощь')
    keyboard.add(button1, button2, button3, one_butt, button4)
    bot.reply_to(message, f"👋Добро пожаловать, {user.username}!\nВы успешно зарегистрировались✅\nТелеграм бот на питоне. Вид сбоку.\nХолст. Масло. 🖼",  reply_markup=keyboard)



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
                button3 = types.KeyboardButton('👨‍💻Разработчики')
                button4 = types.KeyboardButton('ℹ️Помощь')
                keyboard.add(button1, button2, button3, button4)
                bot.send_message(message.chat.id, f"Привет, {user.username}\n✅Ты в главном меню",  reply_markup=keyboard)
        elif message.text == "👨‍💻Разработчики":
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            bt = types.KeyboardButton('⬅️Назад')
            keyboard.add(bt)
            bot.reply_to(message, f"👨‍💻Разработчики👨‍💻\n@Nilandvi\n@hochypitsu",  reply_markup=keyboard)
        elif message.text == "ℹ️Помощь":
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            bt = types.KeyboardButton('⬅️Назад')
            keyboard.add(bt)
            bot.send_message(message.chat.id, "Добро пожаловать в N&G бот 👋\nВ этом боте ты сможешь найти много полезного✅\nПомимо большого разнообразия различного контента в боте есть ascii художник и встроенная википедия. \nКоманды ты сможешь найти при переходе на различные пункты.\n🔹Чтобы воспользоваться википедией, тебе достаточно написать интересующее тебе слово мне, и я с радостью предоставлю тебе интересующую информацию.\n🔹Чтобы воспользоваться функционалом ascii художника, просто кидай мне фотографию, а там я сам управлюсь и отправлю тебе результат!\n=====\nУдачного тебе пользования ботом! \nВ случае обнаружения недоработки или бага, зайди в меню разработчиков и напиши нам о недоработке, может быть мы ее пофиксим!\n", reply_markup=keyboard)
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


bot.polling()
