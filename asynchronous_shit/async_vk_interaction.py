import aiohttp

class VkSaver:
    url = "https://api.vk.com/method/"

    def __init__(self, token: str, version="5.131"):
        self.params = {"access_token": token, "v": version}
        self.session = aiohttp.ClientSession()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def get_user_list(
        self, city, sex, age_from, age_to, offset
    ):
        get_user_id_url = self.url + "users.search"
        user_params = {
            "city": city,
            "sex": sex,
            "age_from": age_from,
            "age_to": age_to,
            "offset": offset,
        }
        async with self.session.get(get_user_id_url, params={**self.params, **user_params}) as response:
            result = await response.json()

            if "error" in result or result["response"]["count"] == 0:
                return None
            else:
                return result["response"]["items"]

    async def get_list_of_album_ids(
        self, owner_id, offset
    ):
        self.owner_id = owner_id
        get_album_url = self.url + "photos.getAlbums"
        album_params = {"owner_id": owner_id, "offset": offset, "need_system": 1}
        async with self.session.get(get_album_url, params={**self.params, **album_params}) as response:
            result = await response.json()
            ids = [item["id"] for item in result["response"]["items"]]

            if "error" in result or result["response"]["count"] == 0:
                return None
            else:
                return ids

    async def get_toprated_photos(
        self, album_id
    ):
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

        async def photos_iterator():
            async with self.session.get(get_photos_url, params={**self.params, **album_params}) as response:
                photos_list = (await response.json())["response"]["items"]

                toprated_list = sorted(
                    photos_list, key=lambda x: x["likes"]["count"], reverse=True
                )[:3]

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
                yield result
        return photos_iterator()

        async with self.session.get(get_photos_url, params={**self.params, **album_params}) as response:
            photos_list = (await response.json())["response"]["items"]

            toprated_list = sorted(
                photos_list, key=lambda x: x["likes"]["count"], reverse=True
            )[:3]

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
