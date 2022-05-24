import telebot
import requests
from telebot import types
import sqlite3
from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import datetime


# Авторизация бота:
bot = telebot.TeleBot('5105850661:AAH4qB5Tt7gv9C-adfeLTSInvqThEUwVK_k')
print('Бот создался')


# Создание кнопок
start_keyboard = types.InlineKeyboardMarkup()
# Кнопка 1 и 2
button_get_lesson1 = types.InlineKeyboardButton(text='Получить цитату', callback_data='button_get_lesson1')
button_get_lesson2 = types.InlineKeyboardButton(text='Получить информацию о себе', callback_data='button_get_lesson2')
# Добавляем кнопки
start_keyboard.add(button_get_lesson1)
start_keyboard.add(button_get_lesson2)

def send_lesson(message):
    print('Идём за цитатой')
    response = requests.get('https://finewords.ru/sluchajnaya?_=1652723055484')
    print('Получили ответ от сайта с цитатой, статус ответа:', response.status_code)
    response_text: str = response.text.replace('</p>', '').replace('<p>', '').replace('<br />', '\n').replace('<br/>', '\n')

    bot.send_message(message.chat.id, response_text, reply_markup=start_keyboard)
    print(message.chat.id)
    print(f'Ответ для {message.chat.first_name} ({message.chat.username}): {response_text}')


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    username: str
    date: str


print('СОздаём БД')
engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)
print('БД создали')


with Session(engine) as session:
    statement = select(User)
    users = session.exec(statement).all()
    print(users)


@bot.message_handler(commands=['start'])
def start(message):
    send_lesson(message)

    with Session(engine) as session:
        statement = select(User).where(User.id == message.chat.id)
        users = session.exec(statement).all()
        print(users)
        if not len(users):
            user1 = User(
                id=message.chat.id,
                first_name=message.chat.first_name,
                username=f'{message.chat.id} - {message.chat.username}',
                date=str(datetime.now())
            )
            session.add(user1)
            session.commit()


def update_users(message):
    with Session(engine) as session:
        statement = select(User).where(User.id == message.chat.id)
        user_in_db = session.exec(statement).first()

        user_in_db.date = str(datetime.now())
        session.add(user_in_db)
        session.commit()

def info(message):
    statement = select(User).where(User.id == message.chat.id)
    results = session.exec(statement)
    user = results.first()
    bot.send_message(message.chat.id, f'Я пробил информацию:\n'
                                      f'\nТы милашечка!\n'
                                      f'Id пользователя: {message.from_user.id}'
                                      f'\nИмя: {message.chat.first_name}'
                                      f'\nНик: {message.chat.username}'
                                      f'\nПоследняя цитата: {user.date}',
                     reply_markup=start_keyboard)


@bot.callback_query_handler(func=lambda c:c.data)
def answer_callback(callback):
    print('Новый колбек', callback.data)
    if callback.data == 'button_get_lesson1':
        send_lesson(callback.message)
        update_users(callback.message)
    elif callback.data == 'button_get_lesson2':
        info(callback.message)


bot.polling()
