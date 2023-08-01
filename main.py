import logging
import time
import os
from random import randrange

import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from dotenv import load_dotenv

# Import custom modules and classes
from resourses import *
from VK_bot_interaction import VKBot

# Set up logging configuration to handle errors
logging.basicConfig(level=logging.ERROR)

# Load environment variables from .env file
load_dotenv()

# Get the VK group token from the environment variable
token = os.getenv("GROUP_TOKEN")

# Create VK API object and VKBot instance
vk = vk_api.VkApi(token=token)
vkbot = VKBot()

# Set up VK Long Poll to listen for incoming messages
longpoll = VkLongPoll(vk)

# Get the long poll server details from VK API
res = vk.method("messages.getLongPollServer")

# Get the initial keyboard layouts for interaction
keyboard_first = vkbot.show_keyboard_first()
keyboard_main = vkbot.show_keyboard_main()

try:
    # Try to establish a connection with VK Long Poll server
    connect = requests.get(
        f"https://{res['server']}?"
        f"act=a_check&key={res['key']}&ts={res['ts']}&wait=25&mode=2&version=3"
    )
    if connect.status_code == 200:
        print("Соединение с VK установлено")
except Exception as Error:
    print(Error)

# Listen for incoming events from VK Long Poll
for event in longpoll.listen():

    # Check if the event is a new incoming message directed to the bot
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        
        # Check if the message is the starting command "💓 Начать 💓"
        if event.text == "💓 Начать 💓":
            # Send the initial message to the user
            vkbot.write_msg(event.user_id, f"Может быть это твоя любовь?", keyboard_first)
            # Fetch and send the first potential match to the user
            vkbot.ids += vkbot.go_first(event.user_id)

        # Check if the message is the "💔 Дальше" command
        elif event.text == "💔 Дальше":
            # Check if there are already potential matches in the list
            if not vkbot.ids:
                vkbot.write_msg(event.user_id, f"Давай подберем тебе пару", keyboard_main)
                vkbot.ids += vkbot.go_first(event.user_id)
            else:
                # Send a random phrase to the user and fetch the next potential match
                vkbot.write_msg(
                    event.user_id, f"{phrases[randrange(len(phrases))]}", keyboard_main
                )
                vkbot.go_next(event.user_id)

        # Check if the message is the "😍 Посмотреть избранное 😍" command
        elif event.text == "😍 Посмотреть избранное 😍":
            # Get the list of user's favorite matches and send it to the user
            favourite_list = vkbot.vk_db.get_favourites_list(event.user_id)
            if not favourite_list:
                vkbot.write_msg(
                    event.user_id,
                    f"В избранном пока пусто, попробуй добавить кого-то",
                    keyboard_main,
                )
            else:
                fav_links = "\n".join(["https://vk.com/id" + str(i) for i in favourite_list])
                vkbot.write_msg(
                    event.user_id,
                    f"😍 Лучшие из лучших 😍 \n \n {fav_links}",
                    keyboard_main,
                )

        # Check if the message is the "❤ Сохранить в избранном" command
        elif event.text == "❤ Сохранить в избранном":
            # Check if there are potential matches to save to favorites
            if not vkbot.ids:
                vkbot.write_msg(
                    event.user_id, f"Давай сначала подберем тебе пару", keyboard_main
                )
                vkbot.ids += vkbot.go_first(event.user_id)
            else:
                # Save the current match to user's favorites and fetch the next potential match
                vkbot.write_msg(event.user_id, f"Сохранено, едем дальше", keyboard_main)
                match = vkbot.vk_db.query_match(
                    event.user_id, vkbot.ids[vkbot.person_counter]["id"]
                )
                vkbot.vk_db.add_to_favourite(match)
                vkbot.go_next(event.user_id)

        # Check if the message is the "🙈 В черный список 🙈" command
        elif event.text == "🙈 В черный список 🙈":
            # Check if there are potential matches to add to the black list
            if not vkbot.ids:
                vkbot.write_msg(
                    event.user_id,
                    f"Некого добавлять в черный список, ищем",
                    keyboard_main,
                )
                vkbot.ids += vkbot.go_first(event.user_id)
            else:
                # Add the current match to user's black list and fetch the next potential match
                vkbot.write_msg(
                    event.user_id,
                    f"Этого человека больше не будет в выдаче, едем дальше",
                    keyboard_main,
                )
                match = vkbot.vk_db.query_match(
                    event.user_id, vkbot.ids[vkbot.person_counter]["id"]
                )
                vkbot.vk_db.add_to_black_list(match)
                time.sleep(0.5)
                vkbot.vk_db.get_black_list(event.user_id)
                vkbot.go_next(event.user_id)

        # If the message does not match any of the above commands, prompt the user to start the search
        else:
            vkbot.write_msg(
                event.user_id, f"Не понял тебя, начнем поиск?", keyboard_first
            )
