from fastapi import Security, security
from fastapi.security import HTTPAuthorizationCredentials
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


class TokenService:
    def __init__(self, async_session: Union[AsyncSession, sessionmaker]):
        self.async_session = async_session

    @staticmethod
    def generate_access_token():
        expiry = datetime.utcnow() + timedelta(weeks=1)  # Token expires in 1 week
        access_token = secrets.token_urlsafe(32)
        return access_token, expiry

    async def create_and_store_access_token(self, user_id: int):
        access_token, expiry = self.generate_access_token()
        async with self.async_session() as session:
            token_entry = AccessToken(access_token=self.hash_token(access_token, os.getenv('SECRET_KEY')), user_id=user_id, expiry=expiry)
            session.add(token_entry)
            try:
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
        return access_token

    @staticmethod
    def hash_token(token: str, salt: str):
        return hashlib.sha256(token.encode() + salt.encode()).hexdigest()

    async def get_current_user_id(self, token: HTTPAuthorizationCredentials = Security(security)):
        async with self.async_session() as session:
            result = await session.execute(
                select(AccessToken).where(AccessToken.access_token == self.hash_token(token.credentials, os.getenv('SECRET_KEY')))
            )
            access_token = result.scalar_one_or_none()

            if access_token:
                return access_token.user_id
            return None


