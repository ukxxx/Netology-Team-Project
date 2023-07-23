import logging
import time
from random import randrange
from datetime import date

import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from dotenv import load_dotenv

from vk_interaction import VkSaver
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from Database.VKdb import VKDataBase
from resourses import *
import os

from VK_bot_interaction import VK_bot

logging.basicConfig(level=logging.DEBUG)

load_dotenv()
token = os.getenv("GROUP_TOKEN")
vk = vk_api.VkApi(token=token)
vkbot = VK_bot()
longpoll = VkLongPoll(vk)
res = vk.method("messages.getLongPollServer")
try:
    connect = requests.get(
        f"https://{res['server']}?"
        f"act=a_check&key={res['key']}&ts={res['ts']}&wait=25&mode=2&version=3"
    )
    if connect.status_code == 200:
        print("Соединение с VK установлено")
except Exception as Error:
    print(Error)

for event in longpoll.listen():

    if event.type == VkEventType.MESSAGE_NEW and event.to_me:

        keyboard_first = vkbot.show_keyboard_first()

        if event.text == "💓 Начать 💓":
            vkbot.write_msg(event.user_id, f"Может быть это твоя любовь?", keyboard_first)
            keyboard_main = vkbot.show_keyboard_main()
            vkbot.ids += vkbot.go_first(event.user_id)

        elif event.text == "💔 Дальше":
            keyboard_main = vkbot.show_keyboard_main()
            vkbot.write_msg(
                event.user_id, f"{phrases[randrange(len(phrases))]}", keyboard_main
            )
            vkbot.go_next(event.user_id)

        elif event.text == "😍 показать Избранное 😍":
            keyboard_main = vkbot.show_keyboard_main()
            favourite_list = vkbot.vk_db.get_favourites_list(event.user_id)
            fav_links = '\n'.join(["https://vk.com/id"+str(i) for i in favourite_list])
            vkbot.write_msg(event.user_id, f"😍 Лучшие из лучших 😍 \n {fav_links}", keyboard_main)

        elif event.text == "❤ Сохранить в избранном":
            ids = vkbot.ids
            keyboard_main = vkbot.show_keyboard_main()
            vkbot.write_msg(event.user_id, f"Сохранен в избранном", keyboard_main)
            time.sleep(0.5)
            match = vkbot.vk_db.query_match_id(event.user_id, ids[vkbot.person_counter]["id"])
            vkbot.vk_db.add_to_favourite(match)

        else:
            vkbot.write_msg(event.user_id, f"Привет! Начнем?", keyboard_first)