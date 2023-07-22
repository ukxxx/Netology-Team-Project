import requests
import os
from random import randint
from dotenv import load_dotenv

load_dotenv()

token2 = os.getenv("GROUP_TOKEN")


class VkSaver:
    url = "https://api.vk.com/method/"

    def __init__(self, token: str, version="5.131"):
        self.params = {"access_token": token, "v": version}

    def send_photos(self, token, owner_id):
        get_message_upload_serv = self.url + "photos.getMessagesUploadServer"
        params = {
            "access_token": token,
            "v": "5.131",
            "group_id": 221556634
        }
        upl_serv_url = requests.get(get_message_upload_serv, params=params).json()
        photo_list = list((self.get_toprated_photos(owner_id)).values())
        photo_list_to_send_to_main = []
        for photo in photo_list:
            img_data = requests.get(photo).content
            image_name = str(randint(1, 100)) + '.jpeg'
            data = upl_serv_url["response"]["upload_url"]
            send = requests.post(data, files={'photo': (image_name, img_data)}).json()
            server = send['server']
            photo = send['photo']
            hash = send['hash']
            save_message = self.url + "photos.saveMessagesPhoto"
            save_params = {
                "access_token": os.getenv("GROUP_TOKEN"),
                "v": "5.131",
                "group_id": 221556634,
                "server": server,
                "photo": photo,
                "hash": hash
            }
            res = requests.get(save_message, params={**save_params}).json()

            photo_list_to_send_to_main.append([res['response'][0]['id'], res['response'][0]['owner_id']])

        return photo_list_to_send_to_main

    def get_user_data(self, user_id):
        get_user_data = self.url + "users.get"
        user_params = {"user_ids": user_id, "fields": "city, sex, bdate"}

        user = requests.get(get_user_data, params={**self.params, **user_params}).json()

        return user["response"][0]

    def get_user_list(
        self, city, sex, age_from, age_to, count=10, offset=0
    ):  # Принимает параметры для поиска и возвращает список словарей с данными пользователей
        get_user_id_url = self.url + "users.search"
        user_params = {
            "city": city,
            "sex": sex,
            "age_from": age_from,
            "age_to": age_to,
            "has_photo": 1,
            "is_closed": False,
            "can_access_closed": True,
            "relation": 6,
            "count": count,
            "offset": offset,
        }
        result = requests.get(
            get_user_id_url, params={**self.params, **user_params}
        ).json()

        if "error" in result or result["response"]["count"] == 0:
            return None
        else:
            return result["response"]["items"]

    def get_toprated_photos(
        self, owner_id
    ):  # Принимает айди альбома и возвращает словарь со ссылками на три наиболее оцененные фотографии
        self.owner_id = owner_id
        get_photos_url = self.url + "photos.get"
        priority_old_photos = "wzyrqpoxms"
        # toprated_list = []
        result = {}
        album_profile_params = {
            "owner_id": self.owner_id,
            "album_id": "profile",
            "photo_sizes": 1,
            "extended": 1,
        }

        album_params = {
            "owner_id": self.owner_id,
            "album_id": -7,
            "photo_sizes": 1,
            "extended": 1,
        }

        photos_profile_list = requests.get(
            get_photos_url, params={**self.params, **album_profile_params}
        ).json()["response"]["items"]
        try:
            photos_list = requests.get(
                get_photos_url, params={**self.params, **album_params}
            ).json()["response"]["items"]

            combined_photos_list = photos_profile_list + photos_list
        except Exception as er:
            combined_photos_list = photos_profile_list
            print(er)
        toprated_list = sorted(
            combined_photos_list, key=lambda x: x["likes"]["count"], reverse=True
        )[
            :3
        ]  # Сортируем список по значениям likes.count и отрезаем 3 наибольших значения

        for (
            photo
        ) in (
            toprated_list
        ):  # Выбираем только самые большие фотографии по двум алгоритмам
            max_size = 0
            for size in photo["sizes"]:
                counter_old_photos = 9
                if size["height"] > 0:
                    if size["height"] > max_size:
                        result[photo["id"]] = size["url"]
                        max_size = size["height"]
                else:
                    if priority_old_photos.index(size["type"]) < counter_old_photos:
                        result[photo["id"]] = size["url"]
                        counter_old_photos = priority_old_photos.index(size["type"])

        return result
