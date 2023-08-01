# VK Matchmaking Bot

This is a simple matchmaking bot for VK (VKontakte) social media platform. The bot uses VK API to perform matchmaking, find potential matches, and allows users to view and save their favorite matches.

## Features

- Matchmaking process based on user age and location.
- View potential matches one by one and move to the next match.
- Save a potential match to favorites for future reference.
- View the list of saved favorite matches.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- VK Group token
- VK Personal token

### Installation

1. Clone the repository to your local machine:

```shell
git clone https://github.com/ukxxx/VK_dating_bot.git
```

2.  Install the required libraries:

```shell
pip install -r requirements.txt
```

3.  Create a .env file in the project root directory and add the following environment variables:

```python
GROUP_TOKEN=your_group_token
PERSONAL_TOKEN=your_personal_token
```

4.  Set up the VK Database and create the necessary tables by running the VKdb.py script.

### Usage

To start the bot, run the main script:

```shell
python main.py
```

Once the bot is running, it will listen for user messages and respond to commands.

* To start the matchmaking process, click on "💓 Начать 💓".
* To view the next potential match, click on "💔 Дальше".
* To view the list of saved favorite matches, click on "😍 Посмотреть Избранное 😍".
* To save the current potential match to favorites, click on "❤ Сохранить в избранном".
* To exclude the current user from the output and add him to the blacklist, click on "🙈 В черный список 🙈"

### Credits

The matchmaking algorithm and VK API interaction code are inspired by various VK bot development tutorials and examples.

### License

This project is licensed under the MIT License - see the LICENSE file for details.
