import os
from sqlalchemy.orm import sessionmaker
from models import create_tables, User, Photo, Match, Favourite
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()


class VKDataBase:

    def __init__(self):

        dialect = 'postgresql'
        login = os.getenv('POSTGRESQL_LOGIN')
        password = os.getenv('POSTGRESQL_PASSWORD')
        self.engine = create_engine(f"{dialect}://{login}:{password}@localhost:5432/VK_dating_bot")
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def create_tables(self):
        create_tables(self.engine)
        print('таблицы созданы')

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
        user = User(vk_id=vk_id, first_name=first_name, last_name=last_name, age=age, sex=sex, city=city)
        self.session.add(user)
        self.session.commit()
        self.session.close()


    def save_photo(self, photo):

        pass

    def save_match(self):
        pass

    def add_to_favourite(self):
        pass

    def delete(self):
        self.session.query(Photo).delete()
        self.session.query(Favourite).delete()
        self.session.query(Match).delete()
        self.session.query(User).delete()
        self.session.commit()
        self.session.close()

vkdb = VKDataBase()
# vkdb.delete()
vkdb.create_tables()