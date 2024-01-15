from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from database.tables import AccessToken
from datetime import datetime, timedelta
import hashlib
import secrets
import os
from dotenv import load_dotenv
from sqlalchemy import select
from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.session import sessionmaker

load_dotenv()


class TokenModel:
    def __init__(self, async_session: Union[AsyncSession, sessionmaker], orm_obj: AccessToken = None, access_token: str = None):
        self.async_session = async_session
        self.orm_obj = orm_obj

    def generate_access_token(self):
        self.expiry = datetime.utcnow() + timedelta(weeks=1)  # Token expires in 1 week
        self.access_token = secrets.token_urlsafe(32)
        return self.access_token, self.expiry

    async def create_and_store_access_token(self, user_id: int):
        self.generate_access_token()
        async with self.async_session() as session:
            token_entry = AccessToken(access_token=self.hash_token(self.access_token, os.getenv('SECRET_KEY')), user_id=user_id, expiry=self.expiry)
            session.add(token_entry)
            try:
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
        return self.access_token

    @staticmethod
    def hash_token(token: str, salt: str):
        return hashlib.sha256(token.encode() + salt.encode()).hexdigest()

    async def get_current_token(self, token: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        async with self.async_session() as session:
            result = await session.execute(
                select(AccessToken).where(AccessToken.access_token == self.hash_token(token.credentials, os.getenv('SECRET_KEY')))
            )
            self.orm_obj = result.scalar_one_or_none()
            return self


