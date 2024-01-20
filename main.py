import telebot
from telebot import types
import datetime
import time

token = '6978321555:AAFLNx50X-t0mPIlHAQRE0GTIC75ioYU2sk'
bot = telebot.TeleBot(token)


def send_message(chat_id, text):
    bot.send_message(chat_id, text)


def send_message_at_time(chat_id, text, hour, minute, day, month):
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
    bot.send_message(chat_id, f"Хорошо, я уведомлю Вас в {hour1}:{minute1} {day1}.{month1} о Вашей встрече.")
    while True:
        now = datetime.datetime.now()
        if now.hour == hour and now.minute == minute and now.day == day and now.month == month:
            send_message(chat_id, text)
            break
        time.sleep(60)


@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    text = "Привет! Я могу отправить напоминалку в нужное Вам время." \
           " Введите через пробел название Вашей напоминалки, время в формате ЧЧ:ММ (например, 09:00) " \
           "и дату в формате ДД.ММ (например, 05.12)."
    bot.send_message(chat_id, text)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text
    try:
        timedate = text.split(' ')
        name = ""
        for i in range(len(timedate)-2):
            name += timedate[i] + " "
        name = name.rstrip()
        hour, minute = map(int, timedate[len(timedate)-2].split(':'))
        day, month = map(int, timedate[len(timedate)-1].split('.'))
        send_message_at_time(chat_id, f"Ваше напоминание \"{name}\" сработало! Удачи Вам!", hour, minute, day, month)
    except ValueError:
        bot.send_message(chat_id, "Неверный формат времени или даты. Введи время в формате ЧЧ:ММ"
                                  " (например, 09:00) и дату в формате ДД.ММ (например, 05.12).")


bot.polling(none_stop=True)
