import json
import logging
from random import randrange
import vk_api
from vk_api.keyboard import VkKeyboard
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
    connect = requests.get(f"https://{res['server']}?act=a_check&key={res['key']}&ts={res['ts']}&wait=25&mode=2&version=3")
    if connect.status_code == 200:
        print('Соединение с ботом установлено')
except Exception as ex:
    print(ex)


keyboard = VkKeyboard(one_time=False, inline=False)
keyboard.add_button("💓 Начать 💓")
keyboard.add_button("💔 Дальше")
keyboard.add_button("❤ Сохранить в избранном")
keyboard.add_line()
keyboard.add_button("😍 Избранное")
keyboard = keyboard.get_keyboard()


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7), 'keyboard': keyboard})


def send_photo(user_id, photo_url):
    vk.method('messages.send', {'user_id': user_id, 'attachment': f"photo{user_id}_{photo_url}", 'random_id': randrange(10 ** 7), 'keyboard': keyboard})  # допилить


def set_params_to_match(user):
    params_to_match = {
        "city": user["city"]["id"],
        "sex": user["sex"],
        "age_from": count_age(user["bdate"]),
        "age_to": count_age(user["bdate"])
    }
    return params_to_match


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text

            if request == "💓 Начать 💓":
                write_msg(event.user_id, f"НАЧНЕМ")
                vksaver.get_user_data(event.user_id)

            elif request == "💔 Дальше":
                write_msg(event.user_id, f"ТУТ_БУДЕТ_НОВЫЙ_ЧЕЛОВЕК")
                user = vksaver.get_user_data(event.user_id)
                params = set_params_to_match(user)
                ids = vksaver.get_user_list(**params)
                print(ids)
                albums_id = vksaver.get_list_of_album_ids(ids[0]['id'])
                top_photos = vksaver.get_toprated_photos(albums_id)
                send_photo(event.user_id, top_photos)
            elif request == "😍 Избранное":
                write_msg(event.user_id, f"ТУТ_БУДЕТ_ИЗБРАННОЕ")
            elif request == "❤ Сохранить в избранном":
                write_msg(event.user_id, f"Сохранен в избранном")
            else:
                write_msg(event.user_id, f"Не понял вашего ответа...")
                