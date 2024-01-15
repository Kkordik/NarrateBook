from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import select
from database.tables import OAuthClient
from typing import Union
import bcrypt


class OAuthClientModel:
    def __init__(self, async_session: Union[AsyncSession, sessionmaker], orm_obj: OAuthClient = None):
        self.async_session = async_session
        self.orm_obj = orm_obj
        

    async def get_redirect_uri(self, client_id: str) -> str:
        async with self.async_session() as session:
            result = await session.execute(select(OAuthClient).where(OAuthClient.client_id == client_id))
            self.orm_obj = result.scalar_one_or_none()
            return self.orm_obj.redirect_uri if self.orm_obj else None

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
            self.orm_obj = result.scalar_one_or_none()

            if self.orm_obj and self.verify_client_secret(provided_secret, self.orm_obj.client_secret):
                return True
            return False
