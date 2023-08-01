# Import required libraries
import logging
import os
import time
from random import randrange
from datetime import date

import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from dotenv import load_dotenv

# Import other modules and classes
from vk_interaction import VkSaver
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from Database.VKdb import VKDataBase
from resourses import phrases


# Setup logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables from .env file
load_dotenv()

# Global variables
ids = []
db_data = {}
db_data_list = []
person_counter = 0
chunk_counter = 1
chunk_size = 10
user_states = {}

# Function to show the initial keyboard to the user
def show_keyboard_first():
    # Creates a VkKeyboard object for the initial keyboard
    keyboard_first = VkKeyboard(one_time=True, inline=False)
    keyboard_first.add_button("💓 Начать 💓", VkKeyboardColor.POSITIVE)
    keyboard_first = keyboard_first.get_keyboard()
    return keyboard_first

# Function to show the main keyboard to the user
def show_keyboard_main():
    # Creates a VkKeyboard object for the main keyboard
    keyboard_main = VkKeyboard(one_time=True, inline=False)
    keyboard_main.add_button("💔 Дальше", VkKeyboardColor.NEGATIVE)
    keyboard_main.add_button("❤ Сохранить в избранном", VkKeyboardColor.POSITIVE)
    keyboard_main.add_line()
    keyboard_main.add_button("😍 Посмотреть Избранное 😍", VkKeyboardColor.PRIMARY)
    keyboard_main = keyboard_main.get_keyboard()
    return keyboard_main

# Fetch the VK group token and personal token from environment variables
token = os.getenv("GROUP_TOKEN")
p_token = os.getenv("PERSONAL_TOKEN")

# Create VK Database object and initialize the database tables
vk_db = VKDataBase()
vk_db.delete()
vk_db.create_tables()

# Create VkSaver object for VK API interaction
vksaver = VkSaver(p_token)

# Initialize VK API objects for group and personal tokens
vk = vk_api.VkApi(token=token)
vk_pers = vk_api.VkApi(token=p_token)

# Set up Long Polling for VK group
longpoll = VkLongPoll(vk)

# Fetch the Long Poll server URL and connect to VK API
res = vk.method("messages.getLongPollServer")
try:
    connect = requests.get(
        f"https://{res['server']}?"
        f"act=a_check&key={res['key']}&ts={res['ts']}&wait=25&mode=2&version=3"
    )
    if connect.status_code == 200:
        print("Соединение с VK установлено")
except Exception as Error:
    print(Error)


def count_age(bdate):
    """
    Calculate the age based on the provided birth date (bdate) in the format 'dd.mm.yyyy'.

    Parameters:
        bdate (str): The birth date in the format 'dd.mm.yyyy'.

    Returns:
        int or None: The calculated age if the birth date is valid and provided, None otherwise.
    """
    if len(bdate) > 5:  # Check if the birth date is properly formatted (dd.mm.yyyy)
        day, month, year = bdate.split(".")  # Split the date into day, month, and year components
        age = (
            date.today().year  # Get the current year
            - int(year)  # Subtract the birth year from the current year
            - ((date.today().month, date.today().day) < (int(month), int(day)))  # Adjust age based on the birth month and day
        )
        return age  # Return the calculated age
    else:
        # If the birth date is not valid or not provided, send an error message to the user
        write_msg(
            event.user_id,
            "У тебя не указан год рождения, поэтому поиск невозможен",
            show_keyboard_first(),
        )
        return None  # Return None to indicate an invalid or missing birth date


def write_msg(user_id, message, keyboard):
    """
    Send a message to a user with the specified content and keyboard.

    Parameters:
        user_id (int): The ID of the user to whom the message will be sent.
        message (str): The content of the message to be sent.
        keyboard (VkKeyboard): The keyboard to be attached to the message.

    Note:
        VkKeyboard is a custom class used to create custom keyboards for VK messages.
    """
    vk.method(
        "messages.send",
        {
            "user_id": user_id,  # ID of the user to send the message to
            "message": message,  # Content of the message
            "random_id": randrange(10**7),  # Random ID to identify the message
            "keyboard": keyboard,  # The custom keyboard to be attached to the message
        },
    )



def set_params_to_match(user):
    """
    Set the parameters for finding a match based on the user's profile.

    Parameters:
        user (dict): A dictionary containing user profile information.

    Returns:
        dict: A dictionary containing the parameters for finding a match.

    Note:
        The 'user' dictionary should contain at least the following keys:
        - 'sex': Gender (1 for female, 2 for male).
        - 'city': A dictionary with the 'id' key representing the user's city ID.
        - 'bdate': The user's birth date in the format 'dd.mm.yyyy'.

    If the user's 'sex' is 1 (female), it is changed to 2 (male) to find opposite-sex matches.
    If the user's 'city' is missing, the default city ID 1 (Moscow) is used for the search.
    The 'age_from' and 'age_to' parameters are calculated based on the user's birth date
    using the 'count_age' function to search for users within the same age range.
    """
    if user["sex"] == 1:  # If the user's gender is female, change to male for opposite-sex matches
        user["sex"] = 2
    else:
        user["sex"] = 1

    try:
        user["city"]
    except KeyError:
        # If the user's city is not specified, search for matches in Moscow by default
        write_msg(
            event.user_id,
            "В твоем профиле не указан город, поэтому ищем в Москве",
            show_keyboard_first(),
        )
        user["city"] = {"id": 1}

    # Set the parameters for finding a match based on the user's profile
    params_to_match = {
        "city": user["city"]["id"],  # ID of the user's city for location-based search
        "sex": user["sex"],  # Desired gender for matching (1 for female, 2 for male)
        "age_from": count_age(user["bdate"]),  # Minimum age for matching
        "age_to": count_age(user["bdate"]),  # Maximum age for matching
    }
    return params_to_match


def send_photo(user_id, ow_id, keyboard):
    """
    Send top-rated photos of a user to another user.

    Parameters:
        user_id (int): The ID of the user who will receive the photos.
        ow_id (int): The ID of the user whose top-rated photos will be sent.
        keyboard (VkKeyboard): The keyboard to be shown with the message.

    Note:
        The function uses the 'vksaver' object to get the top-rated photos of the user
        with the given 'ow_id'. It then sends these photos to the user with the given
        'user_id' using the 'vk' object's 'messages.send' method.

        The 'keyboard' parameter is an instance of the 'VkKeyboard' class that defines
        the keyboard layout to be shown with the message.
    """
    res = vksaver.send_photos(token, ow_id)
    photo_id = res[0][0]
    photo_id1 = res[1][0]
    photo_id2 = res[2][0]
    owner_id = res[0][1]

    # Send the top-rated photos of the user to the target user using the 'messages.send' method
    vk.method(
        "messages.send",
        {
            "user_id": user_id,  # ID of the user who will receive the photos
            "attachment": f"photo{owner_id}_{photo_id},photo{owner_id}_{photo_id1},photo{owner_id}_{photo_id2}",
            "random_id": randrange(10**7),  # Random ID for the message
            "keyboard": keyboard,  # The keyboard layout to be shown with the message
        },
    )


def send_match_message(ids, user_id):
    """
    Send a match message to the user.

    Parameters:
        ids (list): A list of dictionaries containing user data.
        user_id (int): The ID of the user who will receive the match message.

    Note:
        The function constructs a personalized match message using the user data
        from the 'ids' list and sends it to the user with the given 'user_id'.

        The 'ids' list contains dictionaries, each representing a potential match
        with keys like 'first_name', 'last_name', and 'id'.

        The 'profile_link' is a link to the profile of the matched user on VK.
    """
    # Get the first name, last name, and VK ID of the matched user from the 'ids' list
    name = f'{ids[person_counter]["first_name"]} {ids[person_counter]["last_name"]}'
    profile_link = "https://vk.com/id" + f'{ids[person_counter]["id"]}'

    # Construct the match message
    message = f"{name}, \n {profile_link}"

    # Send the match message to the user using the 'write_msg' function with the main keyboard
    write_msg(user_id, message, show_keyboard_main())



def go_first(user_id):  # функция отправки фото для первого использования "Начать"
    """
    Perform the first match for a user and send photos to initiate the interaction.

    Parameters:
        user_id (int): The ID of the user initiating the match.

    Returns:
        list: A list of dictionaries containing user data for potential matches.

    Note:
        The function starts the matchmaking process for a user by performing the
        first match and sending photos of the matched users to the user with the
        given 'user_id'.

        The function uses other helper functions like 'get_user_data', 'set_params_to_match',
        'get_user_list', 'get_toprated_photos', 'send_match_message', 'save_user',
        'save_photo', 'save_match', 'send_photo', and 'show_keyboard_main'.

        The 'params' and 'person_counter' variables are declared as global to keep
        track of the search parameters and the current position in the 'ids' list
        across multiple function calls.
    """
    global params, person_counter

    # Get user data and set parameters for matchmaking using helper functions
    user = vksaver.get_user_data(user_id)
    params = set_params_to_match(user)
    ids = vksaver.get_user_list(**params, count=chunk_size)

    # Get top-rated photos for the first matched user
    top_photos = vksaver.get_toprated_photos(ids[person_counter]["id"])
    p_id = list(top_photos.values())

    try:
        # Save the first user's data in the database using 'save_user' function
        user1 = vk_db.save_user(
            user["id"],
            user["first_name"],
            user["last_name"],
            params["age_from"],
            user["sex"],
            params["city"],
        )
        print(f'{user["first_name"]} {user["last_name"]} добавлен в Базу Данных')
    except Exception as ex:
        print("try user1 ex", ex)

    # If the first matched user has less than 3 photos, proceed to the next user
    if len(p_id) < 3:
        go_next(user_id)
        return ids

    # Send the match message to the user
    send_match_message(ids, user_id)

    try:
        # Save the data of the second matched user in the database using 'save_user' function
        user2 = vk_db.save_user(
            ids[person_counter]["id"],
            ids[person_counter]["first_name"],
            ids[person_counter]["last_name"],
            params["age_from"],
            params["sex"],
            params["city"],
        )
        print(
            f'{ids[person_counter]["first_name"]} {ids[person_counter]["last_name"]} добавлен в Базу Данных'
        )
        # Save the photos of the second user in the database using 'save_photo' function
        for i in p_id:
            vk_db.save_photo(user2, i)
            print(f"Фото добавлено в Базу Данных")
        # Save the match between the first and second users in the database using 'save_match' function
        vk_db.save_match(user1, user2)
        print("Match добавлен")
    except Exception as Error:
        print("try user2 ex", Error)

    # Send photos of the second matched user to the user initiating the match
    send_photo(event.user_id, ids[person_counter]["id"], show_keyboard_main())
    return ids


def go_next(user_id):
    """
    Move to the next potential match for the user and perform necessary actions.

    Parameters:
        user_id (int): The ID of the user initiating the match.

    Returns:
        list: A list of dictionaries containing user data for potential matches.

    Note:
        The function moves to the next potential match for the user and performs
        various actions such as checking if the user's profile is closed, retrieving
        top-rated photos, sending match messages, and saving user data and photos
        in the database using helper functions.

        The 'person_counter', 'ids', and 'chunk_counter' variables are declared as global
        to keep track of the current position in the list of potential matches and the
        chunk size for fetching new matches across multiple function calls.

        The function uses helper functions like 'get_user_list', 'get_toprated_photos',
        'send_match_message', 'save_user', 'save_photo', and 'save_match'.
    """
    global person_counter, ids, chunk_counter

    # Move to the next potential match
    person_counter += 1

    # Wait for a short duration to avoid API request throttling
    time.sleep(0.5)

    # Retrieve the next chunk of potential matches using 'get_user_list'
    ids = vksaver.get_user_list(**params, offset=chunk_counter * chunk_size)

    # Wait for a short duration to avoid API request throttling
    time.sleep(0.5)

    # Check if the current user's profile is closed, if so, move to the next user
    if ids[person_counter]["is_closed"] is True:
        go_next(user_id)
        return

    # Get the top-rated photos of the next matched user
    top_photos = vksaver.get_toprated_photos(ids[person_counter]["id"])
    p_id = list(top_photos.values())

    # If the next matched user has less than three photos, move to the next user
    if len(p_id) < 3:
        go_next(user_id)
        return ids

    # If we have reached the end of the current chunk, reset the counter and move to the next chunk
    if person_counter == len(ids):
        person_counter = 0
        chunk_counter += 1

    try:
        # Send match message to the user with the next matched user's data using 'send_match_message'
        send_match_message(ids, user_id)

        # Save the data of the next matched user in the database using 'save_user' function
        user2 = vk_db.save_user(
            ids[person_counter]["id"],
            ids[person_counter]["first_name"],
            ids[person_counter]["last_name"],
            params["age_from"],
            params["sex"],
            params["city"],
        )
        print(
            f'{ids[person_counter]["first_name"]} {ids[person_counter]["last_name"]} добавлен в Базу Данных'
        )

        # Save the top-rated photos of the next matched user in the database using 'save_photo'
        for i in p_id:
            vk_db.save_photo(user2, i)
            print(f"Фото добавлено в базу")

        # Save the match between the user initiating the match and the next matched user using 'save_match'
        vk_db.save_match(vk_db.get_user_params(event.user_id), user2)
        print("Мatch добавлен в базу данных")
    except Exception as Error:
        print("Ошибка в функции go_next", Error)

    return ids


for event in longpoll.listen():
    """
    Main event loop for handling user interactions and matchmaking process.

    Note:
        The loop listens for new messages from users through the VK API's long polling mechanism.
        It then processes user input and performs actions based on the received message.
        The loop handles different commands, such as starting the matchmaking process, navigating
        to the next potential match, viewing favorites, and adding matches to favorites.

        The loop utilizes various helper functions, such as 'write_msg', 'go_first', 'go_next',
        and functions from the VK API, such as 'get_favourites_list', 'query_match_id', and others.

        The loop keeps running indefinitely, processing user input and performing matchmaking
        actions based on the received commands.
    """
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        # Check if the event is a new message directed to the bot

        if event.text == "💓 Начать 💓":
            # If the user sends the command to start matchmaking, initiate the process

            # Send a greeting message to the user
            write_msg(event.user_id, f"Может быть это твоя любовь?", show_keyboard_first())

            # Initiate the matchmaking process by calling 'go_first' function
            ids += go_first(event.user_id)

        elif event.text == "💔 Дальше":
            # If the user wants to see the next potential match

            if not ids:
                # If there are no potential matches yet, start the matchmaking process first
                write_msg(event.user_id, f"Может быть это твоя любовь?", show_keyboard_first())
                ids += go_first(event.user_id)
            else:
                # Send a random phrase to the user indicating the continuation of the matchmaking process
                write_msg(event.user_id, f"{phrases[randrange(len(phrases))]}", show_keyboard_main())
                
                # Move to the next potential match by calling 'go_next' function
                go_next(event.user_id)

        elif event.text == "😍 Посмотреть Избранное 😍":
            # If the user wants to view their favorites list

            # Retrieve the user's favorites list from the database
            favourite_list = vk_db.get_favourites_list(event.user_id)

            if not favourite_list:
                # If the favorites list is empty, inform the user to add someone to favorites
                write_msg(event.user_id, f"В избранном пока пусто, попробуй добавить кого-то", show_keyboard_main())
            else:
                # Format the favorites list as clickable links and send it to the user
                fav_links = "\n".join(["https://vk.com/id" + str(i) for i in favourite_list])
                write_msg(event.user_id, f"😍 Лучшие из лучших 😍 \n \n {fav_links}", show_keyboard_main())

        elif event.text == "❤ Сохранить в избранном":
            # If the user wants to add the current potential match to favorites

            if not ids:
                # If there are no potential matches yet, start the matchmaking process first
                write_msg(event.user_id, f"Давай сначала подберем тебе пару", show_keyboard_first())
                ids += go_first(event.user_id)
            else:
                # Send a confirmation message to the user
                write_msg(event.user_id, f"Сохранено, едем дальше", show_keyboard_main())

                # Save the match to favorites in the database using 'add_to_favourite' function
                match = vk_db.query_match_id(event.user_id, ids[person_counter]["id"])
                vk_db.add_to_favourite(match)

                # Move to the next potential match
                go_next(event.user_id)

        else:
            # If the user sends an unrecognized command, ask if they want to start the matchmaking process
            write_msg(event.user_id, f"Не понял тебя, начнем поиск?", show_keyboard_first())

