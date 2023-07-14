import json
import logging
from random import randrange

import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType


logging.basicConfig(level=logging.DEBUG)

with open('vk_credentials.json', 'r') as file:
    token = json.loads(file.read())['group_token']
print(token)
vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)

keyboard = VkKeyboard(one_time=False, inline=False)
keyboard.add_button("💔 Дальше")
keyboard.add_button("❤ Сохранить в избранном")
keyboard.add_line()
keyboard.add_button("😍 Избранное")
keyboard = keyboard.get_keyboard()


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7), 'keyboard': keyboard})


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text

            if request == "💔 Дальше":
                write_msg(event.user_id, f"ТУТ_БУДЕТ_НОВЫЙ_ЧЕЛОВЕК")
            elif request == "😍 Избранное":
                write_msg(event.user_id, f"ТУТ_БУДЕТ_ИЗБРАННОЕ")
            elif request == "❤ Сохранить в избранном":
                write_msg(event.user_id, f"Сохранен в избранном")
            else:
                write_msg(event.user_id, f"Не понял вашего ответа...")