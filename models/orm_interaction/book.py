from database.tables import Book
from dotenv import load_dotenv
from sqlalchemy import select
from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.session import sessionmaker
from typing import List

load_dotenv()


class BookModel:
    def __init__(self, async_session: Union[AsyncSession, sessionmaker], orm_obj: Book = None):
        self.async_session = async_session
        self.orm_obj = orm_obj

    async def get_user_books(self, user_id) -> List[Book]:
        async with self.async_session() as session:
            result = await session.execute(select(Book).where(Book.user_id == user_id))
            return result.all()


