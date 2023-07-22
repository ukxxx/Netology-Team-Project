import os
from sqlalchemy.orm import sessionmaker
from Database.models import create_tables, User, Photo, Match, Favourite
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()


class VKDataBase:
    def __init__(self):
        dialect = "postgresql"
        login = os.getenv("POSTGRESQL_LOGIN")
        password = os.getenv("POSTGRESQL_PASSWORD")
        self.engine = create_engine(
            f"{dialect}://{login}:{password}@localhost:5432/VK_dating_bot"
        )
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def create_tables(self):
        create_tables(self.engine)
        print("таблицы созданы")

    def check(self):
        for c in self.session.query(User).all():
            print(c)

        for c in self.session.query(Photo).all():
            print(c)

        for c in self.session.query(Match).all():
            print(c)

        # for c in self.session.query(Favourite).all():
        #     print(c)

        self.session.close()

    def save_user(self, vk_id, first_name, last_name, age, sex, city):
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
        photo = Photo(vk_id=user.vk_id, photo=photo)
        self.session.add(photo)
        self.session.commit()
        return photo

    def save_match(self, user, user2):
        match = Match(vk_id=user.vk_id, user_id=user2.vk_id)
        self.session.add(match)
        self.session.commit()
        return match

    def add_to_favourite(self, match):
        favourite = Favourite(match_id=match.match_id)
        self.session.add(favourite)
        self.session.commit()
        return favourite

    def delete(self):
        self.session.query(Photo).delete()
        self.session.query(Favourite).delete()
        self.session.query(Match).delete()
        self.session.query(User).delete()
        self.session.commit()
        self.session.close()

    def query_user_id(self, vk_id):
        user = self.session.query(User).filter(User.vk_id == vk_id)
        for i in user:
            u_id = i.vk_id
        return u_id

    def query_match_id(self, user_id, target_id):
        match = self.session.query(Match.match_id, Match.vk_id, Match.user_id).filter(Match.vk_id == user_id).\
            filter(Match.user_id == target_id).one()
        return match

    def get_user_params(self, vk_id):
        user = self.session.query(User).filter(User.vk_id == vk_id).one()
        print(type(user))
        return user

    def get_favourites_list(self, user_id):
        favourite_list = self.session.query(Favourite.favourite_id, Favourite.match_id, Match.vk_id, Match.user_id).\
            join(Favourite).filter(Match.vk_id == user_id)
        fav_list = []
        for i in favourite_list:
            fav_list.append(i.user_id)

        return fav_list


if __name__ == "__main__":
    vk_db = VKDataBase()
    vk_db.delete()
    # vk_db.create_tables()

    # user2 = vk_db.save_user(121547, "ppdpp", "oodafaa", 22, 1, 1)
    # user3 = vk_db.save_user(12542727, "ppddpp", "ooadadfaa", 22, 2, 1)
    # photo1 = vk_db.save_photo(user2, "urlphoto1")
    # photo2 = vk_db.save_photo(user3, "urlphoto2")
    # match1 = vk_db.save_match(user2, user3)
    # user_id = vk_db.query_user_id(121547)
    # user_id2 = vk_db.query_user_id(12542727)
    # print(user_id)
    # print(user_id2)
    # match2 = vk_db.query_match_id(user_id, user_id2)
    # vk_db.get_user_params(1225565)
    # vk_db.get_favourites_list(1225565)
    # vk_db.check()
