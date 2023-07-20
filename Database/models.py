import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    # user_id = sq.Column(sq.BigInteger, primary_key=True)
    vk_id = sq.Column(sq.BigInteger, primary_key=True)
    first_name = sq.Column(sq.String(length=100), nullable=False)
    last_name = sq.Column(sq.String(length=100), nullable=False)
    age = sq.Column(
        sq.Integer, nullable=False
    )  
    sex = sq.Column(
        sq.Integer, nullable=False
    )  
    __table_args__ = (
        sq.CheckConstraint("sex IN ('1', '2')", name='check_sex_value'),
        sq.CheckConstraint('age >= 0 AND age <= 999', name='check_age_length'),
    )
    city = sq.Column(sq.Integer, nullable=False)

    def __str__(self):
        return f"User {self.vk_id}: ({self.first_name}, {self.last_name}, {self.age}, {self.sex}, {self.city})"


class Match(Base):
    __tablename__ = "matches"

    match_id = sq.Column(sq.BigInteger, primary_key=True)
    vk_id = sq.Column(sq.BigInteger, sq.ForeignKey("users.vk_id"), nullable=False)
    user_id = sq.Column(sq.BigInteger, sq.ForeignKey("users.vk_id"), nullable=False)

    us = relationship(User, foreign_keys=[vk_id])
    us2 = relationship(User, foreign_keys=[user_id])

    def __str__(self):
        return f"Match {self.match_id}: ({self.vk_id}, {self.user_id})"


class Photo(Base):
    __tablename__ = "photos"

    photo_id = sq.Column(sq.BigInteger, primary_key=True)
    vk_id = sq.Column(sq.BigInteger, sq.ForeignKey("users.vk_id"), nullable=False)
    photo = sq.Column(
        sq.String
    )  # здесь ссылка, поискать конкретно для url другой метод
    # photo_likes = sq.Column(sq.Integer)

    photos = relationship(User, backref="photos")

    def __str__(self):
        return (
            f"Photo {self.photo_id}: ({self.vk_id}, {self.photo})"
        )


class Favourite(Base):
    __tablename__ = "favourite"

    favourite_id = sq.Column(sq.BigInteger, primary_key=True)
    match_id = sq.Column(
        sq.BigInteger, sq.ForeignKey("matches.match_id"), nullable=False
    )

    favourites = relationship(Match, backref="favourite")

    def __str__(self):
        return f"Favourite {self.favourite_id}: {self.match_id}"


def create_tables(engine):
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
