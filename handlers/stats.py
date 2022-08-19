from aiogram import types
from aiogram.dispatcher import FSMContext
from sqlalchemy import select, func

from config import ADMINS
from config import dp
from config import async_session as pg_session
from database.models import User


@dp.message_handler(lambda message: message.from_user.id == ADMINS,
                    commands=['stats'], state='*')
async def stats(message: types.Message, state: FSMContext):
    try:
        async with pg_session() as session:
            await session.begin()

            # count users
            sql = select(func.count(User.id))
            users = await session.execute(sql)
            users = users.scalars().first()

            # count loads
            sql = select(User.loads)
            all_loads = int()
            loads = await session.execute(sql)
            loads = loads.scalars()
            for _ in loads:
                all_loads += _

            # count users loading right now
            sql = select(func.count(User.id)).where(
                User.is_loading == True
            )
            loading_users = await session.execute(sql)
            loading_users = loading_users.scalars().first()

            # send stats
            await message.answer(
                text = f"users: {users}\nloads: {all_loads}\nloading now: {loading_users}"
            )
    except Exception as ERROR:
        print(ERROR)
