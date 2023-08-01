import requests
import os
from random import randint
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# VkSaver Class for VK Dating Bot
class VkSaver:
    # Base URL for VK API
    url = "https://api.vk.com/method/"

    def __init__(self, token: str, version="5.131"):
        # Initialize the VkSaver object with the VK API access token and version
        self.params = {"access_token": token, "v": version}

    def send_photos(self, token, owner_id):
        # Send photos to the VK group using VK API
        # Get the upload server URL for messages from VK API
        get_message_upload_serv = self.url + "photos.getMessagesUploadServer"
        params = {"access_token": token, "v": "5.131", "group_id": 221556634}
        upl_serv_url = requests.get(get_message_upload_serv, params=params).json()

        # Get the list of top-rated photos from the user and send them to the VK group
        photo_list = list((self.get_toprated_photos(owner_id)).values())
        photo_list_to_send_to_main = []
        for photo in photo_list:
            img_data = requests.get(photo).content
            image_name = str(randint(1, 100)) + ".jpeg"

            # Upload the photo to the VK server
            data = upl_serv_url["response"]["upload_url"]
            send = requests.post(data, files={"photo": (image_name, img_data)}).json()
            server = send["server"]
            photo = send["photo"]
            hash = send["hash"]

            # Save the photo message on the VK group
            save_message = self.url + "photos.saveMessagesPhoto"
            save_params = {
                "access_token": os.getenv("GROUP_TOKEN"),
                "v": "5.131",
                "group_id": 221556634,
                "server": server,
                "photo": photo,
                "hash": hash,
            }
            res = requests.get(save_message, params={**save_params}).json()

            # Store the uploaded photo IDs and owner IDs for further processing
            photo_list_to_send_to_main.append(
                [res["response"][0]["id"], res["response"][0]["owner_id"]]
            )

        return photo_list_to_send_to_main

    def get_user_data(self, user_id):
        # Get user data from VK API using the provided user_id
        get_user_data = self.url + "users.get"
        user_params = {"user_ids": user_id, "fields": "city, sex, bdate"}

        # Make the API request and return the user data
        user = requests.get(get_user_data, params={**self.params, **user_params}).json()
        return user["response"][0]

    def get_user_list(
        self, city, sex, age_from, age_to, count=10, offset=0
    ):  # Get a list of users based on search criteria
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

        # Check for errors in the result and return the list of users if available
        if "error" in result or result["response"]["count"] == 0:
            return None
        else:
            return result["response"]["items"]

    def get_toprated_photos(
        self, owner_id
    ):  # Get the top-rated photos for a given user
        self.owner_id = owner_id
        get_photos_url = self.url + "photos.get"
        priority_old_photos = "wzyrqpoxms"
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

        # Get the user's photos from profile and default album
        photos_profile_list = requests.get(
            get_photos_url, params={**self.params, **album_profile_params}
        ).json()["response"]["items"]

        try:
            photos_list = requests.get(
                get_photos_url, params={**self.params, **album_params}
            ).json()["response"]["items"]

            combined_photos_list = photos_profile_list + photos_list
        except Exception as error:
            combined_photos_list = photos_profile_list
            print(f"Возникла ошибка при обработке фотографий: {error}")

        # Sort the photos based on the number of likes in descending order and select the top 3
        toprated_list = sorted(
            combined_photos_list, key=lambda x: x["likes"]["count"], reverse=True
        )[:3]

        # Select the highest resolution photo from each of the top-rated photos
        for photo in toprated_list:
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
