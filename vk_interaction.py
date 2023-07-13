import requests
from pprint import pprint


class VkSaver:
    url = "https://api.vk.com/method/"

    def __init__(self, token: str, version="5.131"):
        self.params = {"access_token": token, "v": version}

    def get_user_list(
        self, city, sex, age_from, age_to, offset
    ):  # Принимает параметры для поиска и возвращает список словарей с данными пользователей
        get_user_id_url = self.url + "users.search"
        user_params = {
            "city": city,
            "sex": sex,
            "age_from": age_from,
            "age_to": age_to,
            "offset": offset,
        }
        result = requests.get(
            get_user_id_url, params={**self.params, **user_params}
        ).json()

        if "error" in result or result["response"]["count"] == 0:
            return None
        else:
            return result["response"]["items"]

    def get_list_of_album_ids(
        self, owner_id, offset
    ):  # Принимает айди пользователя и возвращает список его альбомов
        self.owner_id = owner_id
        get_album_url = self.url + "photos.getAlbums"
        album_params = {"owner_id": owner_id, "offset": offset, "need_system": 1}
        result = requests.get(
            get_album_url, params={**self.params, **album_params}
        ).json()
        ids = [item["id"] for item in result["response"]["items"]]

        if "error" in result or result["response"]["count"] == 0:
            return None
        else:
            return ids

    def get_toprated_photos(
        self, album_id
    ):  # Принимает айди альбома и возвращает словарь со ссылками на три наиболее оцененные фотографии
        self.album_id = album_id
        get_photos_url = self.url + "photos.get"
        priority_old_photos = "wzyrqpoxms"
        toprated_list = []
        result = {}
        album_params = {
            "owner_id": self.owner_id,
            "album_id": self.album_id,
            "photo_sizes": 1,
            "extended": 1,
        }

        photos_list = requests.get(
            get_photos_url, params={**self.params, **album_params}
        ).json()["response"]["items"]

        toprated_list = sorted(
            photos_list, key=lambda x: x["likes"]["count"], reverse=True
        )[:3]  # Сортируем список по значениям likes.count и отрезаем 3 наибольших значения

        for photo in toprated_list:  # Выбираем только самые большие фотографии по двум алгоритмам
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


# temp = VkSaver('vk1.a.7kq5ikN3cbvq844t_GN_lkGOBfp1bhByb8Tp9MT2vgVVkbs_6fiUj-bDGUfL-A74cY8wK0yx1xnBro-Hg6n9t5x3bpDE9fKglPQzxdtA2U0Qn3DnFwEuBzegVxhv0Iznku8p_p5eseAImcMLqYbSi68kQTDoa6VEqddVqd_vu6F-1mEB3UJPBWAAavcHD8g86yeTaVnr61Uer_H9bGqepA')
# user_list = temp.get_user_list(1, 1, 25, 40, 1)
# print(user_list)
# album_ids = temp.get_list_of_album_ids(5, 0)
# print(album_ids)
# photos_list = temp.get_toprated_photos(album_ids[0])
# pprint(photos_list)
