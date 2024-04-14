from threading import Thread
import telebot
from telebot import types
import datetime
import time
from telebot.types import Message

token = ''
bot = telebot.TeleBot(token)

reminder = dict()


def threading_sending(msg, hour, minute, day, month, chat_id, text):
    while True:
        now = datetime.datetime.now()
        if now.hour == hour and now.minute == minute and now.day == day and now.month == month:
            send_message(chat_id, text)
            del reminder[msg.id]
            break
        time.sleep(1)


def send_message(chat_id, text):
    bot.send_message(chat_id, text)


def send_message_at_time(chat_id, text, hour, minute, day, month, name, message: Message):
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
    msg = bot.send_message(chat_id, f"Хорошо, я уведомлю Вас в {hour1}:{minute1} {day1}.{month1} о Вашей встрече.",
                           reply_markup=types.ReplyKeyboardRemove())
    msgid = msg.id
    bot.send_message(chat_id, f"Вы можете найти ответы на эту встречу по этому айди: {msgid}")
    reminder[msgid] = {message.from_user.username: []}
    print(reminder)
    thread = Thread(target=threading_sending(msg, hour, minute, day, month, chat_id, text))
    thread.start()


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


noti_info = {}


@bot.message_handler(commands=['create'])
def handle_message(message):
    chat_id = message.chat.id
    noti_info[chat_id] = {}
    m = bot.send_message(chat_id, "Как назовем Вашу напоминалку?")
    bot.register_next_step_handler(m, check_noti_title)


def check_noti_title(message):
    chat_id = message.chat.id
    title = message.text
    noti_info[chat_id]['title'] = title
    m = bot.send_message(chat_id, "Во сколько Вам напомнить (формат ЧЧ:ММ)?")
    bot.register_next_step_handler(m, check_noti_time)


def check_noti_time(message):
    chat_id = message.chat.id
    timi = message.text
    new_time = datetime.datetime.strptime(timi, '%H:%M')
    noti_info[chat_id]['time'] = {"hour": new_time.hour, "minute": new_time.minute}
    print(noti_info[chat_id]['time']['hour'])
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("Сегодня")
    )
    m = bot.send_message(chat_id,
                         "В какой день Вам напомнить? Нажмите на кнопку 'Сегодня' или введите другую дату в формате ДД.ММ",
                         reply_markup=markup)
    bot.register_next_step_handler(m, check_noti_date)


def check_noti_date(message):
    chat_id = message.chat.id
    date = message.text
    now = datetime.datetime.now()
    if date == "Сегодня":
        day = now.day
        month = now.month
    else:
        new_date = datetime.datetime.strptime(date, '%d.%m')
        day = new_date.day
        month = new_date.month
    noti_info[chat_id]['date'] = {"day": day, "math": month}
    try:
        send_message_at_time(
            chat_id,
            f"Ваше напоминание \"{noti_info[chat_id]['title']}\" сработало! Удачи Вам!",
            noti_info[chat_id]['time']['hour'],
            noti_info[chat_id]['time']['minute'],
            day,
            month,
            noti_info[chat_id]['title'],
            message
        )
    except ValueError:
        bot.send_message(chat_id, "Неверный формат времени или даты. Введи время в формате ЧЧ:ММ"
                                  " (например, 09:00) и дату в формате ДД.ММ (например, 05.12).")


@bot.message_handler(func=lambda msg: msg.reply_to_message and msg.reply_to_message.id in reminder)
def ans(message):
    idi = message.reply_to_message.id
    (reminder[idi][message.from_user.username]).append(message.text)
    print(idi)


def check_answers(msg):
    temp = msg.text.split()
    idi = int(temp[1])
    try:
        if idi in reminder:
            answers = ""
            for i in range(len(reminder[idi][msg.from_user.username])):
                answers += "@" + msg.from_user.username + ": " + reminder[idi][msg.from_user.username][i]
                if i != len(reminder[idi][msg.from_user.username]):
                    answers += "\n"
            print(answers)
            bot.send_message(msg.chat.id, answers)
        else:
            bot.send_message(msg.chat.id, "Данный айди не найден.")
    except Exception as e:
        bot.send_message(msg.chat.id, "Ответов нет")


@bot.message_handler(commands=['answers'])
def show_ans(msg):
    try:
        thread = Thread(target=check_answers(msg))
        thread.start()
    except Exception as e:
        bot.send_message(msg.chat.id, "Вы не ввели ID")


def polling():
    bot.polling(none_stop=True)


Thread(target=polling).start()
