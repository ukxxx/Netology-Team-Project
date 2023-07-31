import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

# Create a base class for declarative models
Base = declarative_base()

# Define the User class to represent user data


class User(Base):
    __tablename__ = "users"

    # Primary key for the user table
    vk_id = sq.Column(sq.BigInteger, primary_key=True)

    # User's first name and last name (maximum length is 100 characters)
    first_name = sq.Column(sq.String(length=100), nullable=False)
    last_name = sq.Column(sq.String(length=100), nullable=False)

    # User's age and sex
    age = sq.Column(sq.Integer, nullable=False)
    sex = sq.Column(sq.Integer, nullable=False)

    # Check constraints to ensure valid sex values (1 for male, 2 for female) and age range (0 to 999)
    __table_args__ = (
        sq.CheckConstraint("sex IN ('1', '2')", name="check_sex_value"),
        sq.CheckConstraint("age >= 0 AND age <= 999", name="check_age_length"),
    )

    # City information (represented as an integer)
    city = sq.Column(sq.Integer, nullable=False)

    def __str__(self):
        return f"User {self.vk_id}: ({self.first_name}, {self.last_name}, {self.age}, {self.sex}, {self.city})"


# Define the Match class to represent match data between users
class Match(Base):
    __tablename__ = "matches"

    # Primary key for the match table
    match_id = sq.Column(sq.BigInteger, primary_key=True)

    # Foreign keys linking matches to users
    vk_id = sq.Column(sq.BigInteger, sq.ForeignKey("users.vk_id"), nullable=False)
    user_id = sq.Column(sq.BigInteger, sq.ForeignKey("users.vk_id"), nullable=False)

    # Relationship with the User class using foreign keys
    us = relationship(User, foreign_keys=[vk_id])
    us2 = relationship(User, foreign_keys=[user_id])

    def __str__(self):
        return f"Match {self.match_id}: ({self.vk_id}, {self.user_id})"


# Define the Photo class to store user photos
class Photo(Base):
    __tablename__ = "photos"

    # Primary key for the photo table
    photo_id = sq.Column(sq.BigInteger, primary_key=True)

    # Foreign key linking photos to users
    vk_id = sq.Column(sq.BigInteger, sq.ForeignKey("users.vk_id"), nullable=False)

    # Photo URL or path represented as a string
    photo = sq.Column(sq.String)

    # Relationship with the User class using backref to access photos from a user object
    photos = relationship(User, backref="photos")

    def __str__(self):
        return f"Photo {self.photo_id}: ({self.vk_id}, {self.photo})"


# Define the Favourite class to store user's favorite matches
class Favourite(Base):
    __tablename__ = "favourite"

    # Primary key for the favorite table
    favourite_id = sq.Column(sq.BigInteger, primary_key=True)

    # Foreign key linking favorites to matches
    match_id = sq.Column(sq.BigInteger, sq.ForeignKey("matches.match_id"), nullable=False)

    # Relationship with the Match class using backref to access favorites from a match object
    favourites = relationship(Match, backref="favourite")

    def __str__(self):
        return f"Favourite {self.favourite_id}: {self.match_id}"


class Blacklist(Base):
    __tablename__ = "blacklist"

    # Primary key for the favorite table
    blacklist_id = sq.Column(sq.BigInteger, primary_key=True)

    # Foreign key linking favorites to matches
    match_id = sq.Column(sq.BigInteger, sq.ForeignKey("matches.match_id"), nullable=False)

    # Relationship with the Match class using backref to access favorites from a match object
    blacklists = relationship(Match, backref="blacklist")

    def __str__(self):
        return f"Favourite {self.blacklist_id}: {self.match_id}"

# Function to create tables based on the defined models


def create_tables(engine):
    # Drop existing tables (if any) and create new ones
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
