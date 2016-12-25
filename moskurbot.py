#! /usr/bin/python
# -*- coding: utf-8 -*-

import telebot
import config
import time
from time import sleep
import eventlet
import requests
import logging


FILENAME_VK = 'last_known_id.txt'
BASE_POST_URL = 'https://vk.com/club134336456?w=wall-134336456_'


CHANNEL_NAME = '@moskur'

bot = telebot.TeleBot(config.API_KEY)

# @bot.message_handler(content_types=["text"])
# def repeat_all_messages(message):
#     bot.send_message(message.chat.id, message.text)

def get_vk_data():

    import vk
    import json

    session = vk.AuthSession(config.VK_APP_ID, config.VK_LOGIN, config.VK_PASS)
    vkapi = vk.API(session, lang='ru')
    
    # get last 10 posts from moskur wall
    s=vkapi.wall.get(owner_id=-config.VK_OID,count=10)
    
    return s[1:]

def send_new_posts(items, last_id):
    for item in items:
        if item['id'] <= last_id:
            break
        link = '{!s}{!s}'.format(BASE_POST_URL, item['id'])
        bot.send_message(CHANNEL_NAME, link)
        # Спим секунду, чтобы избежать разного рода ошибок и ограничений (на всякий случай!)
        time.sleep(1)
    return


def check_new_posts_vk():
    # Пишем текущее время начала
    logging.info('[VK] Started scanning for new posts')
    with open(FILENAME_VK, 'rt') as file:
        last_id = int(file.read())
        if last_id is None:
            logging.error('Could not read from storage. Skipped iteration.')
            return
        logging.info('Last ID (VK) = {!s}'.format(last_id))
    try:
        entries = get_vk_data()
        # Если ранее случился таймаут, пропускаем итерацию. Если всё нормально - парсим посты.
        if entries:
            # запускаем отправку сообщений
            send_new_posts(entries, last_id)
            
            # Записываем новый last_id в файл.
            with open(FILENAME_VK, 'wt') as file:
                file.write(str(entries[0]['id']))
                logging.info('New last_id (VK) is {!s}'.format((entries[0]['id'])))
    except Exception as ex:
        logging.error('Exception of type {!s} in check_new_post(): {!s}'.format(type(ex).__name__, str(ex)))
        pass
    logging.info('[VK] Finished scanning')
    return

if __name__ == "__main__":
    #bot.polling(none_stop=False)
    # item = get_vk_data()[0]
    # print '{!s}{!s}'.format(BASE_POST_URL, item['id'])

    # Избавляемся от спама в логах от библиотеки requests
    #logging.getLogger('requests').setLevel(logging.CRITICAL)
    # Настраиваем наш логгер
    logging.basicConfig(format='[%(asctime)s] %(filename)s:%(lineno)d %(levelname)s - %(message)s', level=logging.INFO,
                        filename='bot_log.log', datefmt='%d.%m.%Y %H:%M:%S')
    check_new_posts_vk()
    logging.info('[App] Script exited.\n')