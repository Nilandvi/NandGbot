import telebot
from telebot import types
import random
from data.config import TOKEN
from data.models import User, Note, Session

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start_handler(message):
    session = Session()
    user = session.query(User).filter_by(chat_id=message.chat.id).first()
    if user is None:
        user = User(chat_id=message.chat.id, username=message.chat.username)
        session.add(user)
        session.commit()
    session.close()
    bot.reply_to(message, f"Привет, {user.username}! Я бот.")

@bot.message_handler(commands=['new_note'])
def new_note_handler(message):
    session = Session()
    user = session.query(User).filter_by(chat_id=message.chat.id).first()
    user = Session().query(User).filter_by(chat_id=message.chat.id).first()
    if not user:
        bot.reply_to(message, "Вы еще не зарегистрировались в боте!")
        return
    
    # Получаем текст новой заметки от пользователя
    bot.reply_to(message, "Введите текст заметки:")
    bot.register_next_step_handler(message, create_new_note, user.id)


def create_new_note(message, user_id):
    session = Session()
    if isinstance(message, telebot.types.Message):
        note = Note(user_id=str(user_id), note_text=message.text)
        session.add(note)
        session.commit()
        bot.send_message(chat_id=message.chat.id, text='Note added successfully!')
    else:
        print(f'Invalid message type: {type(message)}')

@bot.message_handler(commands=['show_notes'])
def show_notes_handler(message):
    # Получаем текущего пользователя
    user = Session().query(User).filter_by(chat_id=message.chat.id).first()
    if not user:
        bot.reply_to(message, "Вы еще не зарегистрировались в боте!")
        return

    # Получаем все заметки текущего пользователя
    notes = Session().query(Note).filter_by(user_id=user.id).all()
    if not notes:
        bot.reply_to(message, "У вас еще нет заметок.")
    else:
        bot.reply_to(message, "Ваши заметки:")
        for note in notes:
            bot.send_message(message.chat.id, note.note_text)

@bot.message_handler(commands=['delete_note'])
def delete_note_handler(message):
    session = Session()
    user = session.query(User).filter_by(chat_id=message.chat.id).first()
    if not user:
        bot.reply_to(message, "Вы еще не зарегистрировались в боте!")
        return

    # Получаем все заметки текущего пользователя
    notes = session.query(Note).filter_by(user_id=user.id).all()
    if not notes:
        bot.reply_to(message, "У вас еще нет заметок.")
        return

    # Просим пользователя выбрать заметку, которую нужно удалить
    note_text = "\n".join([f"{i + 1}. {note.note_text}" for i, note in enumerate(notes)])
    bot.reply_to(message, f"Выберите номер заметки, которую нужно удалить:\n{note_text}")
    bot.register_next_step_handler(message, remove_note, user.id)


def remove_note(message, user_id):
    session = Session()
    if not message.text.isdigit():
        bot.reply_to(message, "Номер заметки должен быть целым числом. Попробуйте еще раз:")
        bot.register_next_step_handler(message, remove_note, user_id)
        return

    # Получаем все заметки текущего пользователя
    notes = session.query(Note).filter_by(user_id=user_id).all()
    if not notes:
        bot.reply_to(message, "У вас еще нет заметок.")
        return

    note_number = int(message.text)
    if note_number < 1 or note_number > len(notes):
        bot.reply_to(message, "Некорректный номер заметки. Попробуйте еще раз:")
        bot.register_next_step_handler(message, remove_note, user_id)
        return

    # Удаляем выбранную заметку
    note_to_delete = notes[note_number - 1]
    session.delete(note_to_delete)
    session.commit()
    bot.reply_to(message, "Заметка успешно удалена!")



@bot.message_handler(content_types=['text'])
def bot_message(message):
    session = Session()
    user = session.query(User).filter_by(chat_id=message.chat.id).first()
    if message.chat.type == "private":
        if message.text == "число":
            bot.send_message(message.chat.id, "Ваше число: " + str(random.randint(0, 1000)))
        if message.text == "расскажи обо мне":
            bot.reply_to(message, f"""Ты {user.username} \n Твой ID в боте: {user.id} \n ID нашего диалога: {user.chat_id} \n Скоро я научусь вести полноценную статистику сообщений и смогу помогать тебе. Жди!""")



bot.polling()