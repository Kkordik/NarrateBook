from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import select
from database.tables import OAuthClient
from typing import Union
import bcrypt


class OAuthClientService:
    def __init__(self, async_session: Union[AsyncSession, sessionmaker]):
        self.async_session = async_session

    async def get_redirect_uri(self, client_id: str):
        async with self.async_session() as session:
            result = await session.execute(select(OAuthClient).where(OAuthClient.client_id == client_id))
            client = result.scalar_one_or_none()
            return client.redirect_uri if client else None

    @staticmethod
    def hash_client_secret(client_secret: str):
        return bcrypt.hashpw(client_secret.encode(), bcrypt.gensalt())

    @staticmethod
    def verify_client_secret(provided_secret, stored_secret):
        # Verify the provided secret against the stored hash
        return bcrypt.checkpw(provided_secret.encode(), stored_secret.encode())

    async def validate_client_credentials(self, client_id: str, provided_secret: str):
        async with self.async_session() as session:
            result = await session.execute(
                select(OAuthClient).where(OAuthClient.client_id == client_id)
            )
            client = result.scalar_one_or_none()

            if client and self.verify_client_secret(provided_secret, client.client_secret):
                return True
            return False
