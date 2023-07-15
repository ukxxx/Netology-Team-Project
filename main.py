import json
import logging
import time
from pprint import pprint
from random import randrange
import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
import requests
from vk_interaction import VkSaver
from datetime import date
today = date.today()


def count_age(bdate):

    if len(bdate) > 5:
        day = int(bdate[:2])
        month = int(bdate[3:5])
        year = int(bdate[6:10])
        age = today.year - year - ((today.month, today.day) < (month, day))
        return age
    else:
        print("не указан год рождения")
        return None


logging.basicConfig(level=logging.DEBUG)

with open('vk_credentials.json', 'r') as file:
    token = json.loads(file.read())['group_token']
with open('vk_credentials.json', 'r') as file:
    p_token = json.loads(file.read())['personal_token']

vk = vk_api.VkApi(token=token)
vksaver = VkSaver(p_token)

longpoll = VkLongPoll(vk)
res = vk.method('messages.getLongPollServer')
try:
    connect = requests.get(f"https://{res['server']}?"
                           f"act=a_check&key={res['key']}&ts={res['ts']}&wait=25&mode=2&version=3")
    if connect.status_code == 200:
        print('Соединение с ботом установлено')
except Exception as ex:
    print(ex)


keyboard = VkKeyboard(one_time=True, inline=False)
keyboard.add_button("💓 Начать 💓", VkKeyboardColor.POSITIVE)
keyboard = keyboard.get_keyboard()


def write_msg(user_id, message):
    vk.method(
        'messages.send',
        {
            'user_id': user_id,
            'message': message,
            'random_id': randrange(10 ** 7),
            'keyboard': keyboard
        }
    )


def send_photo(user_id, photo_url):

    vk.method(
        'messages.send',
        {
            'user_id': user_id,
            'attachment': photo_url,
            'random_id': randrange(10 ** 7),
            'keyboard': keyboard
        }
    )


def clear_chat(user_id):
    pass


def set_params_to_match(user):
    if user["sex"] == 1:  # если пол женский, то в параметры мужской пол
        user["sex"] = 2
    else:
        user["sex"] = 1
    params_to_match = {
        "city": user["city"]["id"],
        "sex": user["sex"],
        "age_from": count_age(user["bdate"]),
        "age_to": count_age(user["bdate"])
    }
    return params_to_match


def go_first(user_id):  # функция отправки фото для первого использования "Начали"
    user = vksaver.get_user_data(user_id)
    params = set_params_to_match(user)
    ids = vksaver.get_user_list(**params)
    albums_id = vksaver.get_list_of_album_ids(ids[-1]['id'])
    top_photos = vksaver.get_toprated_photos(albums_id[0])
    p_id = list(top_photos.keys())
    for i in range(0, 3):
        send_photo(event.user_id, top_photos[int(f'{p_id[i]}')])
        time.sleep(0.5)
    return ids


def go_next(ids):  # функция отправки фото при нажатии на "Дальше". Только нужно добавить counter на id +
    # albums_id = vksaver.get_list_of_album_ids(ids[int(f"{counter}")]['id'])
    albums_id = vksaver.get_list_of_album_ids(ids[-1]['id'])
    top_photos = vksaver.get_toprated_photos(albums_id[0])
    p_id = list(top_photos.keys())
    print("go_next")
    print(p_id)
    for i in range(0, 3):
        send_photo(event.user_id, top_photos[int(f'{p_id[i]}')])
        time.sleep(0.5)


def show_main_keyboard():
    keyboard = VkKeyboard(one_time=False, inline=False)
    keyboard.add_button("💔 Дальше", VkKeyboardColor.NEGATIVE)
    keyboard.add_button("❤ Сохранить в избранном", VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("😍 Избранное")
    keyboard.add_button("Очистить беседу")
    keyboard = keyboard.get_keyboard()
    return keyboard


ids = []


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text
        if request == "💓 Начать 💓":
            time.sleep(0.5)
            write_msg(event.user_id, f"НАЧНЕМ")
            ids += go_first(event.user_id)
            print("Начали")
            pprint(ids)
            keyboard = show_main_keyboard()
        elif request == "💔 Дальше":
            # ids.pop()
            time.sleep(0.5)
            print("Дальше")
            pprint(ids)
            write_msg(event.user_id, f"ТУТ_БУДЕТ_НОВЫЙ_ЧЕЛОВЕК")
            go_next(ids)
        elif request == "😍 Избранное":
            write_msg(event.user_id, f"ТУТ_БУДЕТ_ИЗБРАННОЕ")
        elif request == "❤ Сохранить в избранном":
            write_msg(event.user_id, f"Сохранен в избранном")
        elif request == "Очистить беседу":
            pass
        else:
            write_msg(event.user_id, f"Не понял вашего ответа...")
