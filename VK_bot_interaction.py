import time
from random import randrange
from datetime import date

import vk_api
from dotenv import load_dotenv

# Import custom modules and classes
from VK_API_interaction import VkSaver
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from Database.VKdb import VKDataBase
from resourses import *
import os

# Load environment variables from .env file
load_dotenv()


class VKBot:
    def __init__(self):
        # Get the VK group token and personal token from environment variables
        self.token = os.getenv("GROUP_TOKEN")
        self.p_token = os.getenv("PERSONAL_TOKEN")

        # Create an instance of VKDataBase for handling the database
        self.vk_db = VKDataBase()

        # Clear existing data in the database and create new tables
        self.vk_db.delete()
        self.vk_db.create_tables()

        # Create an instance of VkSaver for handling VK API interactions
        self.vksaver = VkSaver(self.p_token)

        # Initialize VK API objects with the tokens
        self.vk = vk_api.VkApi(token=self.token)
        self.vk_pers = vk_api.VkApi(token=self.p_token)

        # Initialize some variables for the matchmaking process
        self.person_counter = 0
        self.chunk_size = 10
        self.chunk_counter = 1
        self.ids = []

    def show_keyboard_first(self):
        # Define the keyboard layout for the first interaction
        keyboard_first = VkKeyboard(one_time=True, inline=False)
        keyboard_first.add_button("💓 Начать 💓", VkKeyboardColor.POSITIVE)
        self.keyboard_first = keyboard_first.get_keyboard()
        return self.keyboard_first

    def show_keyboard_main(self):
        # Define the main keyboard layout for user interactions
        keyboard_main = VkKeyboard(one_time=False, inline=False)
        keyboard_main.add_button("💔 Дальше", VkKeyboardColor.NEGATIVE)
        keyboard_main.add_button("❤ Сохранить в избранном", VkKeyboardColor.POSITIVE)
        keyboard_main.add_line()
        keyboard_main.add_button("😍 Посмотреть избранное 😍", VkKeyboardColor.PRIMARY)
        keyboard_main.add_button("🙈 В черный список 🙈", VkKeyboardColor.SECONDARY)
        self.keyboard_main = keyboard_main.get_keyboard()
        return self.keyboard_main

    def count_age(self, bdate, user_id):
        # Calculate the age of the user based on their birthdate
        if len(bdate) > 5:
            day, month, year = bdate.split(".")
            age = (
                date.today().year
                - int(year)
                - ((date.today().month, date.today().day) < (int(month), int(day)))
            )
            return age
        else:
            # If birthdate is not provided, inform the user that the search is not possible
            self.write_msg(
                user_id,
                "У вас не указан год рождения, поэтому поиск невозможен",
                self.keyboard_first,
            )
            return None

    def write_msg(self, user_id, message, keyboard):
        # Send a message to the user with the provided keyboard layout
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
        # Set the matching parameters based on the user's data
        if (
            user["sex"] == 1
        ):  # If the user's gender is female, set the matching parameters for male profiles
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
        # Send photos of the potential match to the user
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
        # Send a message to the user with the information about the potential match
        name = f'{self.ids[self.person_counter]["first_name"]} {self.ids[self.person_counter]["last_name"]}'
        profile_link = "https://vk.com/id" + f'{self.ids[self.person_counter]["id"]}'
        message = f"{name}, \n" f" {profile_link}"
        self.write_msg(self.user_id, message, self.keyboard_main)

    def check_blacklist(self):
        # Check if the potential match is in the user's black list
        try:
            self.check_match = self.vk_db.query_match_id(
                self.user_id, self.ids[self.person_counter]["id"]
            )
            print(f"Проверили check_match: {self.check_match}")
            self.black_list = self.vk_db.get_black_list(self.user_id)
            print(f"Проверили black_list: {self.black_list}")
            if self.check_match in self.black_list:
                print(f"Пользователь есть в черном списке, пропускаем")
                self.go_next(self.user_id)
                return
        except Exception as Error:
            self.vk_db.session.rollback()
            print(f"Ошибка при проверке работе функции check_blacklist: {Error}")
            pass

    def go_first(self, user_id):
        # Function for the first interaction with the user and sending the first potential match
        self.user_id = user_id
        self.user = self.vksaver.get_user_data(user_id)
        self.params = self.set_params_to_match(self.user)
        self.ids = self.vksaver.get_user_list(**self.params, count=self.chunk_size)
        self.check_blacklist()
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
                f'{self.user["first_name"]} {self.user["last_name"]} добавлен в базу данных функцией go_first'
            )
        except Exception as Error:
            self.vk_db.session.rollback()
            print(
                f"Ошибка сохранения функцией go_first пользователя 1 в базу данных: {Error})"
            )
        print(self.ids)
        print(self.ids[self.person_counter]["relation"])
        # Check if the current user's profile is closed, if so, move to the next user
        if self.ids[self.person_counter]["is_closed"] is True \
                or self.ids[self.person_counter]["can_access_closed"] is not True:
            self.go_next(self.user_id)
            return

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
                f'{self.ids[self.person_counter]["first_name"]} '
                f'{self.ids[self.person_counter]["last_name"]} добавлен в базу данных функцией go_first'
            )
            for i in self.p_id:
                self.vk_db.save_photo(user2, i)
                print(f"Фото добавлено в Базу Данных функцией go_first")
            self.vk_db.save_match(user1, user2)
            print("Match добавлен функцией go_first")
        except Exception as Error:
            self.vk_db.session.rollback()
            print(
                f"Ошибка сохранения функцией go_first пользователя 2 в базу данных: {Error})"
            )

        self.send_photo(
            self.user_id, self.ids[self.person_counter]["id"], self.keyboard_main
        )
        return self.ids

    def go_next(self, user_id):
        # Function for handling the next potential match when the user wants to see more options
        self.person_counter += 1
        time.sleep(0.5)
        self.ids = self.vksaver.get_user_list(
            **self.params,
            count=self.chunk_size,
            offset=self.chunk_counter * self.chunk_size,
        )
        time.sleep(0.5)
        if self.ids[self.person_counter]["is_closed"] is True:
            self.go_next(user_id)
            return
        self.check_blacklist()
        self.top_photos = self.vksaver.get_toprated_photos(
            self.ids[self.person_counter]["id"]
        )
        self.p_id = list(self.top_photos.values())
        if self.ids[self.person_counter]["is_closed"] is True \
                or self.ids[self.person_counter]["can_access_closed"] is not True:
            self.go_next(self.user_id)
            return
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
                    f'{self.ids[self.person_counter]["first_name"]}'
                    f' {self.ids[self.person_counter]["last_name"]} добавлен в базу данных функцией go_next'
                )
                for i in self.p_id:
                    self.vk_db.save_photo(user2, i)
                    print(f"Фото добавлено в базу данных функцией go_next")
                self.vk_db.save_match(self.vk_db.get_user_params(self.user_id), user2)
                print("Match добавлен в базу данных функцией go_next")
            except Exception as Error:
                self.vk_db.session.rollback()
                print(f"Ошибка сохранения в базу данных функцией go_next: {Error})")
        except Exception as Error:
            self.vk_db.session.rollback()
            print(f"Ошибка отправки данных функцией go_next: {Error})")
        return self.ids
