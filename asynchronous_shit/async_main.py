import asyncio
import aiohttp
from io import BytesIO
from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, Text, PhotoMessageUploader

from async_vk_interaction import VkSaver
from async_read_token import *


async def main():
    group_token, personal_token = await get_token_async()
    bot = Bot(token=group_token)
    photo_uploader = PhotoMessageUploader(bot.api)

    keyboard = (
        Keyboard(one_time=False, inline=False)
        .add(Text("💔 Дальше"))
        .add(Text("❤ Сохранить в избранном"))
        .row()
        .add(Text("😍 Избранное"))
    ).get_json()

    keyboard_first_run = (
        Keyboard(one_time=False, inline=False).add(Text("Начать работу с ботом"))
    ).get_json()

    temp = VkSaver(personal_token)
    user_list = await temp.get_user_list(1, 1, 25, 40, 1)
    album_ids = await temp.get_list_of_album_ids(5, 0)
    photos_list = await temp.get_toprated_photos(album_ids[0])

    async def download_photo(photo_url):
        async with aiohttp.ClientSession() as session:
            async with session.get(photo_url) as response:
                if response.status == 200:
                    return BytesIO(await response.read())

    @bot.on.message(text="[club221556634|@club221556634] 💔 Дальше")
    async def send_keyboard(message):
        async for photo_url in photos_list:
            print(photo_url)
            photo_data = await download_photo(photo_url)
            photo = await photo_uploader.upload(file_source=photo_data)
            await message.answer(attachment=photo)
            await message.answer("ТУТ_БУДЕТ_СЛЕДУЮЩИЙ_КАНДИДАТ", keyboard=keyboard)

    @bot.on.message(text="[club221556634|@club221556634] 😍 Избранное")
    async def send_keyboard(message):
        await message.answer("ТУТ_БУДЕТ_ИЗБРАННОЕ", keyboard=keyboard)

    @bot.on.message(text="[club221556634|@club221556634] ❤ Сохранить в избранном")
    async def send_keyboard(message):
        await message.answer("Сохранен в избранное", keyboard=keyboard)

    @bot.on.message(text="[club221556634|@club221556634] Начать работу с ботом")
    async def hi_handler(message: Message):
        users_info = await bot.api.users.get(message.from_id)
        await message.answer(
            "Привет, {}".format(users_info[0].first_name), keyboard=keyboard_first_run
        )

    await bot.run_polling()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
