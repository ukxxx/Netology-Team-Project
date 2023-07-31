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

load_dotenv()


class VK_bot:
    def __init__(self):
        self.token = os.getenv("GROUP_TOKEN")
        self.p_token = os.getenv("PERSONAL_TOKEN")
        self.vk_db = VKDataBase()
        self.vk_db.delete()
        self.vk_db.create_tables()
        self.vksaver = VkSaver(self.p_token)
        self.vk = vk_api.VkApi(token=self.token)
        self.vk_pers = vk_api.VkApi(token=self.p_token)
        self.person_counter = 0
        self.chunk_size = 10
        self.chunk_counter = 1
        self.ids = []

    def show_keyboard_first(self):
        keyboard_first = VkKeyboard(one_time=True, inline=False)
        keyboard_first.add_button("💓 Начать 💓", VkKeyboardColor.POSITIVE)
        self.keyboard_first = keyboard_first.get_keyboard()
        return self.keyboard_first

    def show_keyboard_main(self):
        keyboard_main = VkKeyboard(one_time=False, inline=False)
        keyboard_main.add_button("💔 Дальше", VkKeyboardColor.NEGATIVE)
        keyboard_main.add_button("❤ Сохранить в избранном", VkKeyboardColor.POSITIVE)
        keyboard_main.add_line()
        keyboard_main.add_button("😍 показать Избранное 😍", VkKeyboardColor.PRIMARY)
        self.keyboard_main = keyboard_main.get_keyboard()
        return self.keyboard_main

    # try:
    #     connect = requests.get(
    #         f"https://{res['server']}?"
    #         f"act=a_check&key={res['key']}&ts={res['ts']}&wait=25&mode=2&version=3"
    #     )
    #     if connect.status_code == 200:
    #         print("Соединение с VK установлено")
    # except Exception as Error:
    #     print(Error)

    def count_age(self, bdate, user_id):
        if len(bdate) > 5:
            day, month, year = bdate.split(".")
            age = (
                date.today().year
                - int(year)
                - ((date.today().month, date.today().day) < (int(month), int(day)))
            )
            return age
        else:
            self.write_msg(
                user_id,
                "У вас не указан год рождения. Поиск невозможен",
                self.keyboard_first,
            )
            return None

    def write_msg(self, user_id, message, keyboard):
        self.vk.method(
            "messages.send",
            {
                "user_id": user_id,
                "message": message,
                "random_id": randrange(10**7),
                "keyboard": keyboard,
            },
        )

    def set_params_to_match(self, user):
        if user["sex"] == 1:  # если пол женский, то в параметры мужской пол
            user["sex"] = 2
        else:
            user["sex"] = 1

        try:
            user["city"]
        except KeyError:
            user["city"] = {"id": 1}

        self.params_to_match = {
            "city": user["city"]["id"],
            "sex": user["sex"],
            "age_from": self.count_age(user["bdate"], user["id"]),
            "age_to": self.count_age(user["bdate"], user["id"]),
        }
        return self.params_to_match

    def send_photo(self, user_id, ow_id, keyboard):
        res = self.vksaver.send_photos(self.token, ow_id)
        photo_id = res[0][0]
        photo_id1 = res[1][0]
        photo_id2 = res[2][0]
        owner_id = res[0][1]

        self.vk.method(
            "messages.send",
            {
                "user_id": user_id,
                "attachment": f"photo{owner_id}_{photo_id},photo{owner_id}_{photo_id1},photo{owner_id}_{photo_id2}",
                "random_id": randrange(10**7),
                "keyboard": keyboard,
            },
        )

    def send_match_message(self):
        name = f'{self.ids[self.person_counter]["first_name"]} {self.ids[self.person_counter]["last_name"]}'
        profile_link = "https://vk.com/id" + f'{self.ids[self.person_counter]["id"]}'
        message = f"{name}, \n" f" {profile_link}"
        self.write_msg(self.user_id, message, self.keyboard_main)

    def go_first(
        self, user_id
    ):  # функция отправки фото для первого использования "Начали"
        # global params, person_counter
        self.user_id = user_id
        self.user = self.vksaver.get_user_data(user_id)
        self.params = self.set_params_to_match(self.user)
        self.ids = self.vksaver.get_user_list(**self.params, count=self.chunk_size)
        self.top_photos = self.vksaver.get_toprated_photos(
            self.ids[self.person_counter]["id"]
        )
        self.p_id = list(self.top_photos.values())

        try:
            user1 = self.vk_db.save_user(
                self.user["id"],
                self.user["first_name"],
                self.user["last_name"],
                self.params["age_from"],
                self.user["sex"],
                self.params["city"],
            )
            print(
                f'{self.user["first_name"]} {self.user["last_name"]} добавлен в Базу Данных'
            )
        except Exception as ex:
            print("try user1 ex", ex)

        if len(self.p_id) < 3:
            self.go_next(self.user_id)
            return self.ids

        self.send_match_message()

        try:
            user2 = self.vk_db.save_user(
                self.ids[self.person_counter]["id"],
                self.ids[self.person_counter]["first_name"],
                self.ids[self.person_counter]["last_name"],
                self.params["age_from"],
                self.params["sex"],
                self.params["city"],
            )
            print(
                f'{self.ids[self.person_counter]["first_name"]} {self.ids[self.person_counter]["last_name"]} добавлен в Базу Данных'
            )
            for i in self.p_id:
                self.vk_db.save_photo(user2, i)
                print(f"Фото добавлено в Базу Данных")
            self.vk_db.save_match(user1, user2)
            print("Match добавлен")
        except Exception as Error:
            print("try user2 ex", Error)

        self.send_photo(
            self.user_id, self.ids[self.person_counter]["id"], self.keyboard_main
        )
        return self.ids

    def go_next(self, user_id):
        # global person_counter, ids, chunk_counter
        self.person_counter += 1
        time.sleep(0.5)
        self.ids = self.vksaver.get_user_list(
            **self.params, offset=self.chunk_counter * self.chunk_size
        )
        time.sleep(0.5)
        if self.ids[self.person_counter]["is_closed"] is True:
            self.go_next(user_id)
            return
        self.top_photos = self.vksaver.get_toprated_photos(
            self.ids[self.person_counter]["id"]
        )
        self.p_id = list(self.top_photos.values())
        if len(self.p_id) < 3:
            self.go_next(self.user_id)
            return self.ids
        if self.person_counter == len(self.ids):
            self.person_counter = 0
            self.chunk_counter += 1

        try:
            self.top_photos = self.vksaver.get_toprated_photos(
                self.ids[self.person_counter]["id"]
            )
            self.p_id = list(self.top_photos.values())
            self.send_match_message()
            self.send_photo(
                self.user_id, self.ids[self.person_counter]["id"], self.keyboard_main
            )

            try:
                user2 = self.vk_db.save_user(
                    self.ids[self.person_counter]["id"],
                    self.ids[self.person_counter]["first_name"],
                    self.ids[self.person_counter]["last_name"],
                    self.params["age_from"],
                    self.params["sex"],
                    self.params["city"],
                )
                print(
                    f'{self.ids[self.person_counter]["first_name"]} {self.ids[self.person_counter]["last_name"]} добавлен в Базу Данных'
                )
                for i in self.p_id:
                    self.vk_db.save_photo(user2, i)
                    print(f"Фото добавлено в базу")
                self.vk_db.save_match(self.vk_db.get_user_params(self.user_id), user2)
                print("match добавлен")
            except Exception as er:
                print("error", er)
        except Exception as ex:
            print("try go next save db", ex)
        return self.ids
