import telebot
from telebot import types
import datetime
import time


from telebot.types import Message

token = ''
bot = telebot.TeleBot(token)

global user_id
reminder = dict()
global msgid


def send_message(chat_id, text):
    bot.send_message(chat_id, text)


def send_message_at_time(chat_id, text, hour, minute, day, month, name, message: Message):
    global msgid
    hour1 = str(hour)
    minute1 = str(minute)
    day1 = str(day)
    month1 = str(month)
    if len(hour1) < 2:
        hour1 = "0" + hour1
    if len(minute1) < 2:
        minute1 = "0" + minute1
    if len(day1) < 2:
        day1 = "0" + day1
    if len(month1) < 2:
        month1 = "0" + month1
    msg = bot.send_message(chat_id, f"Хорошо, я уведомлю Вас в {hour1}:{minute1} {day1}.{month1} о Вашей встрече.")
    msgid = msg.id
    bot.send_message(chat_id, f"Вы можете найти ответы на эту встречу по этому айди: {msgid}")
    reminder[msgid] = {message.from_user.username: []}
    print(reminder)
    while True:
        now = datetime.datetime.now()
        if now.hour == hour and now.minute == minute and now.day == day and now.month == month:
            send_message(chat_id, text)
            del reminder[msg.id]
            break
        time.sleep(1)


@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    text = "Привет! Я могу отправить напоминалку в нужное Вам время.\n" \
           "Введите /help, чтобы узнать список команд."
    bot.send_message(chat_id, text)


@bot.message_handler(commands=['help'])
def handle_help(message):
    chat_id = message.chat.id
    text = "- Чтобы создать напоминалку введите через пробел /create, название напоминалки," \
           " время в формате ЧЧ:ММ и дату в формате ДД.ММ.\n\n- Чтобы посмотреть ответы на вашу напоминалку напишите" \
           " /answers + айди, который пишется при создании напоминалки" \
           " (ответы должны обязательно ссылаться на сообщение бота)."
    bot.send_message(chat_id, text)


@bot.message_handler(commands=['create'])
def handle_message(message):
    chat_id = message.chat.id
    text = message.text
    try:
        timedate = text.split(' ')
        name = ""
        for i in range(len(timedate) - 3):
            name += timedate[i + 1] + " "
        name = name.rstrip()
        hour, minute = map(int, timedate[len(timedate) - 2].split(':'))
        day, month = map(int, timedate[len(timedate) - 1].split('.'))
        send_message_at_time(chat_id, f"Ваше напоминание \"{name}\" сработало! Удачи Вам!", hour, minute, day, month,
                             name, message)
    except ValueError:
        bot.send_message(chat_id, "Неверный формат времени или даты. Введи время в формате ЧЧ:ММ"
                                  " (например, 09:00) и дату в формате ДД.ММ (например, 05.12).")


@bot.message_handler(func=lambda msg: msg.reply_to_message and msg.reply_to_message.id in reminder)
def ans(message):
    idi = message.reply_to_message.id
    (reminder[idi][message.from_user.username]).append(message.text)
    print(idi)


@bot.message_handler(commands=['answers'])
def show_ans(msg):
    temp = msg.text.split()
    idi = int(temp[1])
    if idi in reminder:
        answers = ""
        for i in range(len(reminder[idi][msg.from_user.username])):
            answers += "@" + msg.from_user.username + ": " + reminder[msgid][msg.from_user.username][i]
            if i != len(reminder[idi][msg.from_user.username]):
                answers += "\n"
        print(answers)
        bot.send_message(msg.chat.id, answers)
    else:
        bot.send_message(msg.chat.id, "Данный айди не найден.")


bot.polling(none_stop=True)
