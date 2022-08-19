from aiogram import types
from aiogram.dispatcher import FSMContext
from datetime import datetime
import traceback

from config import dp
from config import async_session as pg_session
from config import bot_logging
from models.user import Users
from strings import ru as ru_strs


@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message, state: FSMContext):
    # reset states
    await state.finish()
    await state.reset_data()

    # get user info
    user_id = message.from_user.id
    username = message.from_user.username
    if username: username = f"@{username}"
    firstname = message.from_user.first_name
    lastname = message.from_user.last_name

    # save or update user
    try:
        async with pg_session() as session:
            await session.begin()
            user = Users(user_id, username, firstname, lastname, False, 0)
            await user.upsert_user(session)
            await session.commit()
    except Exception as ERROR:
        print(traceback.format_exc())
        print(ERROR)

    # send start message
    await message.answer(
        text = ru_strs.start
    )
