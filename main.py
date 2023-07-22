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
    keyboard_main.add_button("❤ Сохранить в избранном", VkKeyboardColor.POSITIVE)
    keyboard_main.add_line()
    keyboard_main.add_button("😍 показать Избранное 😍", VkKeyboardColor.PRIMARY)
    keyboard_main = keyboard_main.get_keyboard()
    return keyboard_main


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
    photo_id = res[0][0]
    photo_id1 = res[1][0]
    photo_id2 = res[2][0]
    owner_id = res[0][1]

    vk.method(
        "messages.send",
        {
            "user_id": user_id,
            "attachment": f"photo{owner_id}_{photo_id},photo{owner_id}_{photo_id1},photo{owner_id}_{photo_id2}",
            "random_id": randrange(10**7),
            "keyboard": keyboard
        }
    )


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
    top_photos = vksaver.get_toprated_photos(ids[person_counter]["id"])
    p_id = list(top_photos.values())

    try:
        user1 = vk_db.save_user(
            user["id"],
            user["first_name"],
            user["last_name"],
            params["age_from"],
            user["sex"],
            params["city"],
        )
        print(f'{user["first_name"]} {user["last_name"]} добавлен в Базу Данных')
    except Exception as ex:
        print("try user1 ex", ex)

    if len(p_id) < 3:
        go_next(user_id)
        return ids

    send_match_message(ids, user_id)

    try:
        user2 = vk_db.save_user(
                ids[person_counter]["id"],
                ids[person_counter]["first_name"],
                ids[person_counter]["last_name"],
                params["age_from"],
                params["sex"],
                params["city"]
        )
        print(f'{ids[person_counter]["first_name"]} {ids[person_counter]["last_name"]} добавлен в Базу Данных')
        for i in p_id:
            vk_db.save_photo(
                user2,
                i
            )
            print(f'Фото добавлено в Базу Данных')
        vk_db.save_match(
            user1,
            user2
        )
        print('Match добавлен')
    except Exception as Error:
        print("try user2 ex", Error)

    send_photo(event.user_id, ids[person_counter]["id"], keyboard_main)
    return ids


def go_next(user_id):

    global person_counter, ids, chunk_counter
    person_counter += 1
    time.sleep(0.5)
    ids = vksaver.get_user_list(**params, offset=chunk_counter * chunk_size)
    time.sleep(0.5)
    if ids[person_counter]["is_closed"] is True:
        go_next(user_id)
        return
    top_photos = vksaver.get_toprated_photos(ids[person_counter]["id"])
    p_id = list(top_photos.values())
    if len(p_id) < 3:
        go_next(user_id)
        return ids
    if person_counter == len(ids):
        person_counter = 0
        chunk_counter += 1

    try:

        top_photos = vksaver.get_toprated_photos(ids[person_counter]["id"])
        p_id = list(top_photos.values())
        send_match_message(ids, user_id)
        send_photo(event.user_id, ids[person_counter]["id"], keyboard_main)

        try:
            user2 = vk_db.save_user(
                ids[person_counter]["id"],
                ids[person_counter]["first_name"],
                ids[person_counter]["last_name"],
                params["age_from"],
                params["sex"],
                params["city"]
            )
            print(f'{ids[person_counter]["first_name"]} {ids[person_counter]["last_name"]} добавлен в Базу Данных')
            for i in p_id:
                vk_db.save_photo(
                    user2,
                    i
                )
                print(f'Фото добавлено в базу')
            vk_db.save_match(
                vk_db.get_user_params(event.user_id),
                user2
            )
            print("match добавлен")
        except Exception as er:
            print('error', er)
    except Exception as ex:
        print("try go next save db", ex)
    return ids


for event in longpoll.listen():

    if event.type == VkEventType.MESSAGE_NEW and event.to_me:

        keyboard_first = show_keyboard_first()

        if event.text == "💓 Начать 💓" and event.user_id not in user_states:
            write_msg(event.user_id, f"Может быть это твоя любовь?", keyboard_first)
            ids += go_first(event.user_id)

        elif event.text == "💔 Дальше":
            keyboard_main = show_keyboard_main()
            write_msg(
                event.user_id, f"{phrases[randrange(len(phrases))]}", keyboard_main
            )
            go_next(event.user_id)

        elif event.text == "😍 показать Избранное 😍":
            keyboard_main = show_keyboard_main()
            favourite_list = vk_db.get_favourites_list(event.user_id)
            fav_links = '\n'.join(["https://vk.com/id"+str(i) for i in favourite_list])
            write_msg(event.user_id, f"😍 Лучшие из лучших 😍 \n {fav_links}", keyboard_main)

        elif event.text == "❤ Сохранить в избранном":
            ids = vksaver.get_user_list(**params, offset=chunk_counter * chunk_size)
            keyboard_main = show_keyboard_main()
            write_msg(event.user_id, f"Сохранен в избранном", keyboard_main)
            time.sleep(0.5)
            match = vk_db.query_match_id(event.user_id, ids[person_counter]["id"])
            vk_db.add_to_favourite(match)

        else:
            write_msg(event.user_id, f"Привет! Начнем?", keyboard_first)
