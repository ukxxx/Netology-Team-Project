from vkbottle.bot import Bot, Message


bot = Bot(token='vk1.a.CLld4ad1X90Em_kENKKCz_6X7F-FgqpQIdPjTfO0yobWtgp7dNFxNdeCAEb_TOQGMaPtuFShfTOA5XzB17mIx6U5MjHlJBrBuo7-nsobfUoTouCqt3shWw3E9nsmR0E2b1mngQRfm0Vk5cwgzJntVc7a_7xHYh1AvsXTKILYDPQBxHuwpGs13fsk_WHg9jsn4kRpGhnOtdfHHizfXdh81A')


@bot.on.message(text="Привет")
async def hi_handler(message: Message):
    users_info = await bot.api.users.get(message.from_id)
    await message.answer("Привет, {}".format(users_info[0].first_name))

bot.run_forever()

