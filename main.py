import json
import logging
from pprint import pprint
from random import randrange
from datetime import date

import requests
import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from vk_interaction import VkSaver
from Database.VKdb import VKDataBase
from resourses import phrases

logging.basicConfig(level=logging.DEBUG)
ids = []
db_data = {}
db_data_list = []
person_counter = 0
chunk_counter = 1
chunk_size = 10

keyboard_first = VkKeyboard(one_time=True, inline=False)
keyboard_first.add_button("💓 Начать 💓", VkKeyboardColor.POSITIVE)
keyboard_first = keyboard_first.get_keyboard()

keyboard_main = VkKeyboard(one_time=False, inline=False)
keyboard_main.add_button("💔 Дальше", VkKeyboardColor.NEGATIVE)
keyboard_main.add_button("❤ Сохранить в избранном", VkKeyboardColor.PRIMARY)
keyboard_main.add_line()
keyboard_main.add_button("😍 Избранное")
keyboard_main.add_button("Очистить беседу")
keyboard_main = keyboard_main.get_keyboard()

with open("vk_credentials.json", "r") as file:
    token = json.loads(file.read())["group_token"]
with open("vk_credentials.json", "r") as file:
    p_token = json.loads(file.read())["personal_token"]

vkdatabase = VKDataBase()

vk = vk_api.VkApi(token=token)
vk_pers = vk_api.VkApi(token=p_token)
vksaver = VkSaver(p_token)
longpoll = VkLongPoll(vk)
res = vk.method("messages.getLongPollServer")
try:
    connect = requests.get(
        f"https://{res['server']}?"
        f"act=a_check&key={res['key']}&ts={res['ts']}&wait=25&mode=2&version=3"
    )
    if connect.status_code == 200:
        print("Соединение с ботом установлено")
except Exception as ex:
    print(ex)


def count_age(bdate):
    if len(bdate) > 5:
        day, month, year = bdate.split(".")
        # day = int(bdate[:2])
        # month = int(bdate[3:5])
        # year = int(bdate[6:10])
        age = (
            date.today().year
            - int(year)
            - ((date.today().month, date.today().day) < (int(month), int(day)))
        )
        return age
    else:
        print("Не указан год рождения")
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
    # upload_url = vk.get_api().photos.getMessagesUploadServer()["upload_url"]
    #
    # attachments = []
    # for photo_url in photo_urls:
    #     response = requests.get(photo_url)
    #     with open("temp.jpg", "wb") as file:  # Вот это
    #         file.write(response.content)  # Вот это
    #     upload_data = requests.post(
    #         upload_url, files={"photo": open("temp.jpg", "rb")}
    #     ).json()  # И вот это мне дико не нравится, но у меня не получилось передавать response.content сразу в джейсон
    #     photo_info = vk.get_api().photos.saveMessagesPhoto(**upload_data)
    #     attachments.append(f"photo{photo_info[0]['owner_id']}_{photo_info[0]['id']}")

    res = vksaver.send_photos(token, ow_id)
    print(ow_id)
    print(res)
    photo_id = res[0][0]
    print(photo_id)
    photo_id1 = res[1][0]
    print(photo_id1)
    photo_id2 = res[2][0]
    print(photo_id2)
    owner_id = res[0][1]
    print(owner_id)
    print([f"photo{owner_id}_{photo_id}", f"photo{owner_id}_{photo_id1}", f"photo{owner_id}_{photo_id2}"])

    vk.method(
        "messages.send",
        {
            "user_id": user_id,
            "attachment": f"photo{owner_id}_{photo_id},photo{owner_id}_{photo_id1},photo{owner_id}_{photo_id2}",  # или через запятую только {photo_id}
            "random_id": randrange(10**7),
            "keyboard": keyboard
        }
    )

# "attachment": f"photo{owner_id}_{photo_id}, {owner_id}_{photo_id1}, {owner_id}_{photo_id2}",
def take_position(user_id):  # забирать id в базу
    # connection = VKDataBase()
    pass


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
    print(ids)
    top_photos = vksaver.get_toprated_photos(ids[0]["id"])
    p_id = list(top_photos.values())
    print(p_id)
    if len(p_id) < 3:
        print('сработал if')
        person_counter += 1
        go_next(user_id)
        return ids
    # top_photos = vksaver.get_toprated_photos(ids[0]["id"])
    # p_id = list(top_photos.values())
    send_match_message(ids, user_id)

    try:
        vkdatabase.save_user(
            user["id"],
            user["first_name"],
            user["last_name"],
            params["age_from"],
            user["sex"],
            params["city"],
        )
        vkdatabase.save_user(
            ids["id"],
            ids["first_name"],
            ids["last_name"],
            params["age_from"],
            params["sex"],
            params["city"],
        )
    except Exception as ex:
        print(ex)
        pass
    send_photo(event.user_id, ids[0]["id"], keyboard_main)
    return ids


def go_next(
    user_id,
):  # функция отправки фото при нажатии на "Дальше". Только нужно добавить person_counter на id +
    global person_counter, ids, chunk_counter

    person_counter += 1

    if person_counter == len(ids):
        person_counter = 0
        ids = vksaver.get_user_list(**params, offset=chunk_counter * chunk_size)
        chunk_counter += 1


    try:
        # top_photos = vksaver.get_toprated_photos(ids[person_counter]["id"])
        # p_id = list(top_photos.values())

        send_match_message(ids, user_id)
        send_photo(event.user_id, ids[person_counter]["id"], keyboard_main)
    except:
        pass


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        if event.text == "💓 Начать 💓":
            write_msg(event.user_id, f"Может быть это твоя любовь?", keyboard_first)
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
        elif event.text == "Очистить беседу":
            clear_chat(event.user_id)
        else:
            write_msg(event.user_id, f"Не понял вашего ответа...", keyboard_main)
        print("проход")
        with open("db_data.json", "w") as f:
            json.dump(db_data_list, f)
