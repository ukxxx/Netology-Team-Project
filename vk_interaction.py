import requests
from pprint import pprint
from random import randint

token2 = "vk1.a.CLld4ad1X90Em_kENKKCz_6X7F-FgqpQIdPjTfO0yobWtgp7dNFxNdeCAEb_TOQGMaPtuFShfTOA5XzB17mIx6U5MjHlJBrBuo7-nsobfUoTouCqt3shWw3E9nsmR0E2b1mngQRfm0Vk5cwgzJntVc7a_7xHYh1AvsXTKILYDPQBxHuwpGs13fsk_WHg9jsn4kRpGhnOtdfHHizfXdh81A"

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
                "access_token": "vk1.a.CLld4ad1X90Em_kENKKCz_6X7F-FgqpQIdPjTfO0yobWtgp7dNFxNdeCAEb_TOQGMaPtuFShfTOA5XzB17mIx6U5MjHlJBrBuo7-nsobfUoTouCqt3shWw3E9nsmR0E2b1mngQRfm0Vk5cwgzJntVc7a_7xHYh1AvsXTKILYDPQBxHuwpGs13fsk_WHg9jsn4kRpGhnOtdfHHizfXdh81A",

                "v": "5.131",
                "group_id": 221556634,
                "server": server,
                "photo": photo,
                "hash": hash
            }
            res = requests.get(save_message, params={**save_params}).json()

# <<<<<<< HEAD
#             ph_list_to_send_to_main.append([res['response'][0]['id'], res['response'][0]['owner_id']])
#         # print(ph_list_to_send_to_main)
#         return ph_list_to_send_to_main
# =======
            photo_list_to_send_to_main.append([res['response'][0]['id'], res['response'][0]['owner_id']])
#
        return photo_list_to_send_to_main
# >>>>>>> cc5abc0eb96306333fe8d6f7ac07aaa67106065a



    # def send_photo_file(self):
    #     r = requests.get("https://sun9-79.userapi.com/c11046/u1225565/-6/w_0b70b720.jpg")
    #     img_data = r.content
    #     # print(r)
    #     # print(img_data)
    #     image_name = '1.jpeg'
    #     data = self.upl_serv_url["response"]["upload_url"]
    #     # files = "photo=@https://vk.com/albums1225565?z=photo1225565_457240935%2Fphotos1225565"
    #     # files = {'photo': "https://sun9-79.userapi.com/c11046/u1225565/-6/w_0b70b720.jpg"}
    #     # files = {'photo': (image_name, img_data)}
    #     send = requests.post(data, files = {'photo': (image_name, img_data)}).json()
    #     self.server = send['server']
    #     self.photo = send['photo']
    #     self.hash = send['hash']
    #     return send


    # def save_messages_photo(self):
    #
    #     save_message = self.url + "photos.saveMessagesPhoto"
    #     params = {
    #         "access_token": "vk1.a.CLld4ad1X90Em_kENKKCz_6X7F-FgqpQIdPjTfO0yobWtgp7dNFxNdeCAEb_TOQGMaPtuFShfTOA5XzB17mIx6U5MjHlJBrBuo7-nsobfUoTouCqt3shWw3E9nsmR0E2b1mngQRfm0Vk5cwgzJntVc7a_7xHYh1AvsXTKILYDPQBxHuwpGs13fsk_WHg9jsn4kRpGhnOtdfHHizfXdh81A",
    #
    #         "v": "5.131",
    #         "group_id": 221556634,
    #         "server": self.server,
    #         "photo": self.photo,
    #         "hash": self.hash
    #     }
    #     res = requests.get(save_message, params={**params}).json()
    #     print(res)
    #     self.photo_id = res['response'][0]['id']
    #     self.owner_id = res['response'][0]['owner_id']


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

    # def get_list_of_album_ids(
    #     self, owner_id
    # ):  # Принимает айди пользователя и возвращает список его альбомов
    #     self.owner_id = owner_id
    #     get_album_url = self.url + "photos.getAlbums"
    #     album_params = {"owner_id": owner_id, "offset": 1, "need_system": 1}
    #     result = requests.get(
    #         get_album_url, params={**self.params, **album_params}
    #     ).json()
    #     ids = [item["id"] for item in result["response"]["items"]]
    #
    #     if "error" in result or result["response"]["count"] == 0:
    #         return None
    #     else:
    #         return ids

    def get_toprated_photos(
        self, owner_id
    ):  # Принимает айди альбома и возвращает словарь со ссылками на три наиболее оцененные фотографии
        self.owner_id = owner_id
        get_photos_url = self.url + "photos.get"
        priority_old_photos = "wzyrqpoxms"
        toprated_list = []
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

        photos_list = requests.get(
            get_photos_url, params={**self.params, **album_params}
        ).json()["response"]["items"]

        combined_photos_list = photos_profile_list + photos_list

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




# if __name__ == "__main__":

#
# temp = VkSaver('vk1.a.7kq5ikN3cbvq844t_GN_lkGOBfp1bhByb8Tp9MT2vgVVkbs_6fiUj-bDGUfL-A74cY8wK0yx1xnBro-Hg6n9t5x3bpDE9fKglPQzxdtA2U0Qn3DnFwEuBzegVxhv0Iznku8p_p5eseAImcMLqYbSi68kQTDoa6VEqddVqd_vu6F-1mEB3UJPBWAAavcHD8g86yeTaVnr61Uer_H9bGqepA')
# # # user_list = temp.get_user_list(1, 1, 35, 35)
# # # temp.get_message_upload_server()
# # # temp.send_photo_file()
# # # temp.save_messages_photo()
# # # pprint(user_list)
# # # album_ids = temp.get_list_of_album_ids(5)
# # # print(album_ids)
# photos_list = temp.get_toprated_photos(789180381)
# # # #
# # res = temp.send_photos(token2, 1089625)
# # print(res)
# # print(temp.send_photos(token2, 789180381))
#
# pprint(photos_list)
