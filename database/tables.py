from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, BigInteger, String, TIMESTAMP, ForeignKey, SMALLINT
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    user_id = Column(BigInteger, primary_key=True)
    date_time = Column(TIMESTAMP, default=func.now())


class Book(Base):
    __tablename__ = 'books'
    book_id = Column(SMALLINT, autoincrement=True, primary_key=True)
    book_title = Column(String(128))
    book_author = Column(String(128))
    book_description = Column(String(128))
    file_id = Column(String(256))
    user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    last_char_id = Column(BigInteger)
    char_len = Column(BigInteger)


class OAuthClient(Base):
    __tablename__ = 'oauth_clients'
    client_id = Column(String, primary_key=True)
    client_secret = Column(String, nullable=False)
    redirect_uri = Column(String)


class AccessToken(Base):
    __tablename__ = 'access_tokens'
    access_token = Column(String, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False, unique=True)
    expiry = Column(TIMESTAMP, nullable=False)
    date_time = Column(TIMESTAMP, default=func.now())
