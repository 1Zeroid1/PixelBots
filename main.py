import telebot
import time
import datetime
from multiprocessing import *
import schedule
from telebot import types

token = '6978321555:AAFLNx50X-t0mPIlHAQRE0GTIC75ioYU2sk'
bot = telebot.TeleBot(token)
global USER_ID
global tm


def start_process():  # Запуск Process
    p1 = Process(target=P_schedule.start_schedule, args=()).start()


class P_schedule():  # Class для работы с schedule
    def start_schedule():  # Запуск schedule
        ######Параметры для schedule######
        schedule.every().day.at(tm).do(P_schedule.send_message1)
        schedule.every(1).minutes.do(P_schedule.send_message2)
        ##################################

        while True:  # Запуск цикла
            schedule.run_pending()
            time.sleep(1)

    ####Функции для выполнения заданий по времени
    def send_message1():
        bot.send_message(USER_ID, 'Отправка сообщения по времени')

    def send_message2():
        bot.send_message(USER_ID, 'Отправка сообщения через определенное время')
    ################


###Настройки команд telebot#########
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Нажали start')
    global USER_ID
    USER_ID = message.user.id
    bot.register_next_step_handler(message, timer)

def timer(message):
    global tm
    tm = message.text
    bot.send_message(message.chat.id, 'Ввели время')


#####################


if __name__ == '__main__':
    start_process()
    try:
        bot.polling(none_stop=True)
    except:
        pass
