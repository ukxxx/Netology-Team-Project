import json
import logging
from pprint import pprint
from random import randrange
from datetime import date

import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from dotenv import load_dotenv

from vk_interaction import VkSaver
from Database.VKdb import VKDataBase
from resourses import *
import os


logging.basicConfig(level=logging.DEBUG)
load_dotenv()

ids = []
db_data = {}
db_data_list = []
person_counter = 0
chunk_counter = 1
chunk_size = 10
# user_states = {}

# with open("vk_credentials.json", "r") as file:
#     token = json.loads(file.read())["group_token"]
# with open("vk_credentials.json", "r") as file:
#     p_token = json.loads(file.read())["personal_token"]

token = os.getenv("GROUP_TOKEN")
p_token = os.getenv("PERSONAL_TOKEN")

vk_db = VKDataBase()
vk_db.delete()
vk_db.create_tables()

vksaver = VkSaver(p_token)

vk = vk_api.VkApi(token=token)
vk_pers = vk_api.VkApi(token=p_token)

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


def count_age(bdate):
    if len(bdate) > 5:
        day, month, year = bdate.split(".")
        age = (
            date.today().year
            - int(year)
            - ((date.today().month, date.today().day) < (int(month), int(day)))
        )
        return age
    else:
        write_msg(event.user_id, "У вас не указан год рождения. Поиск невозможен", keyboard_first)
        return None

def write_msg(user_id, message, keyboard):
    vk.method(
        "messages.send",
        {
            "user_id": user_id,
            "message": message,
            "random_id": randrange(10**7),
            "keyboard": keyboard,
        },
    )

def set_params_to_match(user):
    if user["sex"] == 1:  # если пол женский, то в параметры мужской пол
        user["sex"] = 2
    else:
        user["sex"] = 1

    try:
        user["city"]
    except KeyError:
        user["city"] = {"id": 1}

    params_to_match = {
        "city": user["city"]["id"],
        "sex": user["sex"],
        "age_from": count_age(user["bdate"]),
        "age_to": count_age(user["bdate"]),
    }
    return params_to_match

def send_photo(user_id, ow_id, keyboard):

    res = vksaver.send_photos(token, ow_id)  # вот тут не понял почему возвращает только один список с двумя значениями, а не с тремя.
    photo_id = res[0][0] # Тут надо будет доделать, так как бывает отдается одна или две фотографии, или вообще без фотографии, то есть этот код упадет
    photo_id1 = res[1][0]
    photo_id2 = res[2][0]
    owner_id = res[0][1]

    vk.method(
        "messages.send",
        {
            "user_id": user_id,
            "attachment": f"photo{owner_id}_{photo_id}, {owner_id}_{photo_id1}, {owner_id}_{photo_id2}",  # или через запятую только {photo_id}
            "random_id": randrange(10**7),
            "keyboard": keyboard
        }
    )

def add_favorite(user_id):
    try:
        vk_db.save_user(
            user_id["id"],
            user_id["first_name"],
            user_id["last_name"],
            params["age_from"],
            params["sex"],
            params["city"],
        )
        vk_db.save_match(event.user_id, user_id["id"])
        vk_db.add_to_favourite() # Вот эта ебала ждет мэтч_айди, который хз откуда взять, предыдущая функция возвращает none

    except Exception as Error:
        write_msg(event.user_id, Error, keyboard_main)
        pass

def clear_chat(user_id, chat_id=None):
    pass

def send_match_message(ids, user_id):
    name = f'{ids[person_counter]["first_name"]} {ids[person_counter]["last_name"]}'
    profile_link = "https://vk.com/id" + f'{ids[person_counter]["id"]}'
    message = f"{name}, \n" f" {profile_link}"
    write_msg(user_id, message, keyboard_main)

def go_first(user_id):
    global params
    user = vksaver.get_user_data(user_id)
    params = set_params_to_match(user)
    ids = vksaver.get_user_list(**params, count=chunk_size)
    send_match_message(ids, user_id)

    try:
        vk_db.save_user(
            user["id"],
            user["first_name"],
            user["last_name"],
            params["age_from"],
            user["sex"],
            params["city"],
        )
    except Exception as Error:
        write_msg(event.user_id, Error, keyboard_main)
        pass
    send_photo(event.user_id, ids[0]["id"], keyboard_main)
    return ids

def go_next(user_id,):

    global person_counter, ids, chunk_counter
    person_counter += 1

    if person_counter == len(ids):
        person_counter = 0
        ids = vksaver.get_user_list(**params, offset=chunk_counter * chunk_size)
        chunk_counter += 1

    try:
        send_match_message(ids, user_id)
        send_photo(event.user_id, ids[person_counter]["id"], keyboard_main)
    except:
        pass


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        if event.text == "💓 Начать 💓" and event.user_id not in user_states:
            write_msg(event.user_id, f"Может быть это твоя любовь?", keyboard_first)
            # user_states[event.user_id] = 1
            ids += go_first(event.user_id)
        elif event.text == "💔 Дальше":
            write_msg(
                event.user_id, f"{phrases[randrange(len(phrases))]}", keyboard_main
            )
            go_next(event.user_id)
        elif event.text == "😍 Избранное":
            write_msg(event.user_id, f"ТУТ_БУДЕТ_ИЗБРАННОЕ", keyboard_main)         
        elif event.text == "❤ Сохранить в избранном":
            write_msg(event.user_id, f"Сохранен в избранном", keyboard_main)
            add_favorite(ids[person_counter])
        elif event.text == "Очистить беседу":
            clear_chat(event.user_id)
        else:
            write_msg(event.user_id, f"Привет! Начнем?", keyboard_first)
