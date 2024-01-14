from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import select
from database.tables import User
from typing import Union


class UserService:
    def __init__(self, async_session: Union[AsyncSession, sessionmaker]):
        self.async_session = async_session

    async def add_user(self, user_id: int):
        async with self.async_session() as session:
            user = User(user_id=user_id)
            session.add(user)
            try:
                await session.commit()
            except Exception as e:
                await session.rollback()
                # Handle the exception accordingly
                raise e

    async def get_user(self, user_id: int):
        async with self.async_session() as session:
            result = await session.execute(select(User).where(User.user_id == user_id))
            return result.scalar_one_or_none()
