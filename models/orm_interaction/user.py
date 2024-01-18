from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import select
from database.tables import User
from typing import Union


class UserModel:
    def __init__(self, async_session: Union[AsyncSession, sessionmaker], orm_obj: User = None):
        self.async_session = async_session
        self.orm_obj = orm_obj

    async def add_user(self, user_id):
        async with self.async_session() as session:
            # Check if the user already exists
            exists = await session.execute(
                select(User).where(User.user_id == user_id)
            )
            if exists.scalar_one_or_none():
                return

            # If the user does not exist, add them
            try:
                new_user = User(user_id=user_id)
                session.add(new_user)
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e

    async def get_user(self, user_id: int):
        async with self.async_session() as session:
            result = await session.execute(select(User).where(User.user_id == user_id))
            self.orm_obj = result.scalar_one_or_none()
            return self
