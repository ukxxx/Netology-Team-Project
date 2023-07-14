from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, Text, KeyboardButtonColor
import asyncio

from vk_interaction import VkSaver
from async_read_token import *


group_token, personal_token = asyncio.run(get_token_async())
bot = Bot(token=group_token)
# bot = Bot(token="vk1.a.CLld4ad1X90Em_kENKKCz_6X7F-FgqpQIdPjTfO0yobWtgp7dNFxNdeCAEb_TOQGMaPtuFShfTOA5XzB17mIx6U5MjHlJBrBuo7-nsobfUoTouCqt3shWw3E9nsmR0E2b1mngQRfm0Vk5cwgzJntVc7a_7xHYh1AvsXTKILYDPQBxHuwpGs13fsk_WHg9jsn4kRpGhnOtdfHHizfXdh81A")

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


@bot.on.message(
    text="[club221556634|@club221556634] 💔 Дальше"
)  # Тут надо будет переделать текст, пока не разобрался что делать, чтобы не писать имя группы
async def send_keyboard(message):
    await message.answer("ТУТ_БУДЕТ_СЛЕДУЮЩИЙ_КАНДИДАТ", keyboard=keyboard)


@bot.on.message(text="[club221556634|@club221556634] 😍 Избранное")  # Тут тоже
async def send_keyboard(message):
    await message.answer("ТУТ_БУДЕТ_ИЗБРАННОЕ", keyboard=keyboard)


@bot.on.message(text="[club221556634|@club221556634] ❤ Сохранить в избранном")  # И тут
async def send_keyboard(message):
    await message.answer("Сохранен в избранное", keyboard=keyboard)


@bot.on.message(text="[club221556634|@club221556634] Начать работу с ботом")
async def hi_handler(message: Message):
    users_info = await bot.api.users.get(message.from_id)
    await message.answer(
        "Привет, {}".format(users_info[0].first_name), keyboard=keyboard_first_run
    )


asyncio.run(bot.run_polling())