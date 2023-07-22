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
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
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
user_states = {}


def show_keyboard_first():
    keyboard_first = VkKeyboard(one_time=True, inline=False)
    keyboard_first.add_button("💓 Начать 💓", VkKeyboardColor.POSITIVE)
    keyboard_first = keyboard_first.get_keyboard()
    return keyboard_first

def show_keyboard_main():
    keyboard_main = VkKeyboard(one_time=False, inline=False)
    keyboard_main.add_button("💔 Дальше", VkKeyboardColor.NEGATIVE)
    keyboard_main.add_button("❤ Сохранить в избранном", VkKeyboardColor.PRIMARY)
    keyboard_main.add_line()
    keyboard_main.add_button("😍 Избранное")
    keyboard_main.add_button("Очистить беседу")
    keyboard_main = keyboard_main.get_keyboard()
    return keyboard_main

# keyboard_first = VkKeyboard(one_time=True, inline=False)
# keyboard_first.add_button("💓 Начать 💓", VkKeyboardColor.POSITIVE)
# keyboard_first = keyboard_first.get_keyboard()
# keyboard_main = VkKeyboard(one_time=False, inline=False)
# keyboard_main.add_button("💔 Дальше", VkKeyboardColor.NEGATIVE)
# keyboard_main.add_button("❤ Сохранить в избранном", VkKeyboardColor.PRIMARY)
# keyboard_main.add_line()
# keyboard_main.add_button("😍 Избранное")
# keyboard_main.add_button("Очистить беседу")
# keyboard_main = keyboard_main.get_keyboard()


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

    res = vksaver.send_photos(token, ow_id)
    # print(ow_id)
    # print(res)
    photo_id = res[0][0]
    # print(photo_id)
    photo_id1 = res[1][0]
    # print(photo_id1)
    photo_id2 = res[2][0]
    # print(photo_id2)
    owner_id = res[0][1]

    vk.method(
        "messages.send",
        {
            "user_id": user_id,
            "attachment": f"photo{owner_id}_{photo_id},photo{owner_id}_{photo_id1},photo{owner_id}_{photo_id2}",  # или через запятую только {photo_id}
            "random_id": randrange(10**7),
            "keyboard": keyboard
        }
    )


# def add_favorite(user_id):
#     try:
#         vk_db.save_user(
#             user_id["id"],
#             user_id["first_name"],
#             user_id["last_name"],
#             params["age_from"],
#             params["sex"],
#             params["city"],
#         )
#         vk_db.save_match(event.user_id, user_id["id"])
#         vk_db.add_to_favourite()
#
#     except Exception as Error:
#         write_msg(event.user_id, Error, keyboard_main)
#         pass


def clear_chat(user_id, chat_id=None):
    pass

def send_match_message(ids, user_id):
    name = f'{ids[person_counter]["first_name"]} {ids[person_counter]["last_name"]}'
    profile_link = "https://vk.com/id" + f'{ids[person_counter]["id"]}'
    message = f"{name}, \n" f" {profile_link}"
    write_msg(user_id, message, keyboard_main)



def go_first(user_id):  # функция отправки фото для первого использования "Начали"
    global params, person_counter
    user = vksaver.get_user_data(user_id)
    params = set_params_to_match(user)
    ids = vksaver.get_user_list(**params, count=chunk_size)
    # print(f"go_first_IDS: {ids}")
    top_photos = vksaver.get_toprated_photos(ids[person_counter]["id"])
    print(f'go_first_top_photos: {top_photos}')
    p_id = list(top_photos.values())
    if len(p_id) < 3:
        print('сработал if')
        person_counter += 1
        go_next(user_id)
        return ids

    send_match_message(ids, user_id)

    # try:
    #     # user1 = vk_db.save_user(
    #     #     user["id"],
    #     #     user["first_name"],
    #     #     user["last_name"],
    #     #     params["age_from"],
    #     #     user["sex"],
    #     #     params["city"],
    #     # )
        # user2 = vk_db.save_user(
        #         ids[0]["id"],
        #         ids[0]["first_name"],
        #         ids[0]["last_name"],
        #         params["age_from"],
        #         ids[0]["sex"],
        #         params["city"]
        # )
        # for i in p_id:
        #     vk_db.save_photo(
        #         user2,
        #         i
        #     )
        # vk_db.save_match(
        #     user1,
        #     user2
        # )
    # except Exception as Error:
    #     write_msg(event.user_id, Error, keyboard_main)
    #     pass
    send_photo(event.user_id, ids[0]["id"], keyboard_main)
    return ids

def go_next(user_id):  # теперь после фикса БД тут не работает отправка 3 фото

    global person_counter, ids, chunk_counter
    person_counter += 1
    print(f"go_next: user_id : {user_id}")

    if person_counter == len(ids):
        print('сработал if в go next')
        person_counter = 0

        chunk_counter += 1
    print('1111111')
    ids = vksaver.get_user_list(**params, offset=chunk_counter * chunk_size)
    try:
        print("try_go_next")
        print(ids)
        print(ids[person_counter])
        top_photos = vksaver.get_toprated_photos(ids[person_counter]["id"])
        print(f"try go_next_top_photos {top_photos}")
        p_id = list(top_photos.values())
        print(f"go_next_try: {ids}")
        send_match_message(ids, user_id)
        print(f'go_next_try_person_counter: {ids[person_counter]["id"]}')
        send_photo(event.user_id, ids[person_counter]["id"], keyboard_main)

        # user2 = vk_db.save_user(
        #     ids[0]["id"],
        #     ids[0]["first_name"],
        #     ids[0]["last_name"],
        #     params["age_from"],
        #     ids[0]["sex"],
        #     params["city"]
        # )
        # почему-то второго юзера не сохраняет, наверно не видит params
        # for i in p_id:
        #     vk_db.save_photo(
        #         user2,
        #         i
        #     )
        #
        # vk_db.save_match(
        #     vk_db.get_user_params(event.user_id),
        #     user2
        # )
    except Exception as ex:
        print(ex)
        pass


for event in longpoll.listen():

    if event.type == VkEventType.MESSAGE_NEW and event.to_me:

        keyboard_first = show_keyboard_first()
        if event.text == "💓 Начать 💓" and event.user_id not in user_states:
            write_msg(event.user_id, f"Может быть это твоя любовь?", keyboard_first)
            # user_states[event.user_id] = 1
            ids += go_first(event.user_id)
        elif event.text == "💔 Дальше":
            keyboard_main = show_keyboard_main()
            write_msg(
                event.user_id, f"{phrases[randrange(len(phrases))]}", keyboard_main
            )
            go_next(event.user_id)
        elif event.text == "😍 Избранное":
            keyboard_main = show_keyboard_main()
            write_msg(event.user_id, f"ТУТ_БУДЕТ_ИЗБРАННОЕ", keyboard_main)
        elif event.text == "❤ Сохранить в избранном":
            keyboard_main = show_keyboard_main()
            write_msg(event.user_id, f"Сохранен в избранном", keyboard_main)
            user = vk_db.query_user_id(event.user_id)
            user2 = vk_db.query_user_id(ids[person_counter])
            match = vk_db.query_match_id(user, user2)
            vk_db.add_to_favourite(match)
        elif event.text == "Очистить беседу":
            clear_chat(event.user_id)
        else:
            write_msg(event.user_id, f"Привет! Начнем?", keyboard_first)
