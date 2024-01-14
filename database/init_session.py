import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL_PART = f"://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

async_engine = create_async_engine("mysql+aiomysql"+DATABASE_URL_PART, echo=True)
async_session = sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)
