from aiogram import Bot, Dispatcher
import asyncio
from aiogram.contrib.fsm_storage.redis import RedisStorage2
#import aioredis
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import logging as bot_logging
import os

from database.base import Base


# load env vars
DOTENV_PATH = f"{os.path.dirname(__file__)}/bot.env"
load_dotenv(DOTENV_PATH)


# bot staff
TOKEN = os.getenv('TOKEN')
ADMINS = int(os.getenv('ADMINS'))


# psql
PG_USER = os.getenv('PG_USER')
PG_PASS = os.getenv('PG_PASS')
PG_HOST = os.getenv('PG_HOST')
PG_NAME = os.getenv('PG_NAME')


# pathes
TEMP_VIDEOS = './temp_videos/'
VIDEO_TEMPLATE = '{video_id}.mp4'


# logging
bot_logging.basicConfig(
    level = bot_logging.INFO,
    filename = 'bot.log',
    filemode = 'a',
    format = '%(levelname)s : %(name)s : %(asctime)s - %(message)s'
)

# psql sync session
engine = create_engine(
    f"postgresql+psycopg2://{PG_USER}:{PG_PASS}@{PG_HOST}/{PG_NAME}"
)
session = sessionmaker(
    bind = engine,
    autocommit = False,
    expire_on_commit = False
)


# psql async session
async_engine = create_async_engine(
    f"postgresql+asyncpg://{PG_USER}:{PG_PASS}@{PG_HOST}/{PG_NAME}"
)
async_session = sessionmaker(
    bind = async_engine,
    autocommit = False,
    expire_on_commit = False,
    class_ = AsyncSession
)


# redis fsm storage
#redis = aioredis.from_url('redis://localhost:6379', db=2)
redis_storage = RedisStorage2(
    host = 'localhost',
    port = 6379,
    db = 2
)


# bot
bot = Bot(TOKEN)
bot['db'] = async_session
dp = Dispatcher(
    bot,
    storage = redis_storage
)


# create db tables if running file
if __name__ == "__main__":
    Base.metadata.create_all(engine)
