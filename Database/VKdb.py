import os
from sqlalchemy.orm import sessionmaker
from Database.models import create_tables, User, Photo, Match, Favourite, Blacklist
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# VK Dating Bot Database Class


class VKDataBase:
    def __init__(self):
        dialect = "postgresql"
        login = os.getenv("POSTGRESQL_LOGIN")
        password = os.getenv("POSTGRESQL_PASSWORD")

        # Create a database engine with the provided credentials
        self.engine = create_engine(
            f"{dialect}://{login}:{password}@localhost:5432/VK_dating_bot"
        )

        # Create a session maker bound to the engine
        self.Session = sessionmaker(bind=self.engine)

        # Create a session to interact with the database
        self.session = self.Session()

    def create_tables(self):
        # Call the create_tables function from models.py to create necessary tables in the database
        create_tables(self.engine)

    def check(self):
        # Print all User objects stored in the database
        for c in self.session.query(User).all():
            print(c)

        # Print all Photo objects stored in the database
        for c in self.session.query(Photo).all():
            print(c)

        # Print all Match objects stored in the database
        for c in self.session.query(Match).all():
            print(c)

        # Print all Favourite objects stored in the database
        for c in self.session.query(Favourite).all():
            print(c)

        # Close the session after querying and printing data
        self.session.close()

    def save_user(self, vk_id, first_name, last_name, age, sex, city):
        # Create a new User object and add it to the session
        user = User(
            vk_id=vk_id,
            first_name=first_name,
            last_name=last_name,
            age=age,
            sex=sex,
            city=city,
        )
        self.session.add(user)
        self.session.commit()
        return user

    def save_photo(self, user, photo):
        # Create a new Photo object associated with the given User and add it to the session
        photo = Photo(vk_id=user.vk_id, photo=photo)
        self.session.add(photo)
        self.session.commit()
        return photo

    def save_match(self, user, user2):
        # Create a new Match object representing a match between two users and add it to the session
        match = Match(vk_id=user.vk_id, user_id=user2.vk_id)
        self.session.add(match)
        self.session.commit()
        return match

    def add_to_favourite(self, match):
        # Create a new Favourite object representing a favorite match and add it to the session
        favourite = Favourite(match_id=match.match_id)
        self.session.add(favourite)
        self.session.commit()
        return favourite

    def delete(self):
        # Delete all data from the tables (Photo, Favourite, Match, User) and commit the changes
        self.session.query(Photo).delete()
        self.session.query(Favourite).delete()
        self.session.query(Blacklist).delete()
        self.session.query(Match).delete()
        self.session.query(User).delete()
        self.session.commit()

        # Close the session after deletion and commit
        self.session.close()

    def query_user_id(self, vk_id):
        # Query and return the user_id associated with the given vk_id
        user = self.session.query(User).filter(User.vk_id == vk_id)
        for i in user:
            u_id = i.vk_id
        return u_id

    def query_match(self, user_id, target_id):
        # Query and return the match associated with the given user_id and target_id
        match = (
            self.session.query(Match.match_id, Match.vk_id, Match.user_id)
            .filter(Match.vk_id == user_id)
            .filter(Match.user_id == target_id)
            .one()
        )
        return match

    def query_match_id(self, user_id, target_id):
        # Query and return the match_id associated with the given user_id and target_id
        match = (
            self.session.query(Match.match_id, Match.vk_id, Match.user_id)
            .filter(Match.vk_id == user_id)
            .filter(Match.user_id == target_id)
            .one()
        )

        return match[2]

    def get_user_params(self, vk_id):
        # Query and return the User object associated with the given vk_id
        user = self.session.query(User).filter(User.vk_id == vk_id).one()
        print(type(user))
        return user

    def get_favourites_list(self, user_id):
        # Query and return a list of user_ids for all favorite matches of the given user_id
        favourite_list = (
            self.session.query(
                Favourite.favourite_id, Favourite.match_id, Match.vk_id, Match.user_id
            )
            .join(Favourite)
            .filter(Match.vk_id == user_id)
        )
        fav_list = []
        for i in favourite_list:
            fav_list.append(i.user_id)

        return fav_list

    def add_to_black_list(self, match):
        # Create a new Favourite object representing a favorite match and add it to the session
        blacklist = Blacklist(match_id=match.match_id)
        self.session.add(blacklist)
        self.session.commit()
        return blacklist

    def get_black_list(self, user_id):
        # Query and return a blacklist of the given user_id
        blacklist = (
            self.session.query(
                Blacklist.blacklist_id, Blacklist.match_id, Match.vk_id, Match.user_id
            )
            .join(Blacklist)
            .filter(Match.vk_id == user_id)
        )
        black_list = []

        for i in blacklist:
            black_list.append(i.user_id)
        print(black_list)
        return black_list


# if __name__ == "__main__":
#     vk_db = VKDataBase()
    # vk_db.delete()
    # vk_db.create_tables()
