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

        for c in self.session.query(Favourite).all():
            print(c)

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
        user = self.session.query(User).filter(User.vk_id==vk_id)

        for i in user:
            u_id = i.vk_id

        return u_id

    def query_match_id(self, user_id, target_id):
        # match = self.session.query(User.vk_id, Match.match_id).\
        #     join(User).join(Match).filter(User.vk_id == user_id)
        match = self.session.query(Match.match_id, Match.vk_id, Match.user_id).filter(Match.vk_id == user_id).\
            filter(Match.user_id == target_id).one()
        print(type(match))
        print(match._mapping)
        # favourite = match.match_id
        #
        # for match_id in match:
        #     i = match_id.match_id
        # print(i)
        # print(favourite)
        return match

    def get_user_params(self, vk_id):
        user = self.session.query(User).filter(User.vk_id == vk_id)

        return user

# if __name__ == "__main__":
#     vk_db = VKDataBase()
#     vk_db.delete()
#     vk_db.create_tables()
