from ast import Delete
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
import shortuuid
import subprocess
import os
import re

from config import TEMP_VIDEOS, VIDEO_TEMPLATE
from config import dp, bot
from config import async_session as pg_session
from models.user import Users
from strings import ru as ru_strs


class LoadStates(StatesGroup):
    wait_link = State()


@dp.message_handler(commands=['load'], state='*')
async def load(message: types.Message, state: FSMContext):
    # reset states
    await state.finish()
    await state.reset_data()

    # get user info
    user_id = message.from_user.id
    username = message.from_user.username
    if username: username = f"@{username}"
    firstname = message.from_user.first_name
    lastname = message.from_user.last_name

    # upsert user
    async with pg_session() as session:
        await session.begin()
        user = Users(user_id, username, firstname, lastname, False, 0)
        await user.upsert_user(session)
        await session.commit()

        # check if already loading
        if await user.check_loading(session):
            await message.answer(
                text = ru_strs.wait_link_already
            )
            return

    # send wait link message
    await message.answer(
        text = ru_strs.wait_link
    )

    # set wait link state
    await LoadStates.wait_link.set()


@dp.message_handler(lambda message: message.text and message.text[0] != '/',
                    state=LoadStates.wait_link)
async def wait_link(message: types.Message, state: FSMContext):
    # get info
    video_link = message.text
    user_id = message.from_user.id
    user = Users(user_id, None, None, None, None, None)

    async with pg_session() as session:
        await session.begin()
        # check if already loading
        if await user.check_loading(session):
            await message.answer(
                text = ru_strs.wait_link_already
            )
            return

        # load video
        video_id = shortuuid.uuid()
        video_name = VIDEO_TEMPLATE.format(video_id=video_id)
        video_path = f"{TEMP_VIDEOS}{video_name}"
        is_load = False
        try:
            # set is_loading
            await user.change_load_status(True, session)
            await session.commit()

            # pre validation of video link
            if 'tiktok.' not in video_link:
                await message.answer(
                    text = ru_strs.wait_link_wrong
                )
                await LoadStates.wait_link.set()
                return

            # wait video message and status
            wait_message = await message.answer(
                text = ru_strs.wait_link_wait
            )
            await bot.send_chat_action(
                chat_id = user_id,
                action = 'upload_video'
            )

            # run load process and wait it to end
            loader = subprocess.Popen([
                'yt-dlp',
                '-P',
                TEMP_VIDEOS,
                '-o',
                f"{video_name}",
                video_link
            ],
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE)
            loader.wait()

            # validate video link
            if loader.returncode == 1:
                await user.change_load_status(False, session)
                await session.commit()
                await message.answer(
                    text = ru_strs.wait_link_wrong
                )
                await LoadStates.wait_link.set()
                return
            is_load = True
        except Exception as ERROR:
            print(ERROR)
            is_load = False
            await wait_message.delete()

        # final message
        if is_load:
            # send video and ok text
            with open(video_path, 'rb') as video_file:
                await message.answer(
                    text = ru_strs.wait_link_done
                )
                await message.answer_video(
                    video = video_file
                )
            await wait_message.delete()

            # increase users loads and reset is_loading
            await user.increase_loads(session)
            await user.change_load_status(False, session)
            await session.commit()

            # remove video that send
            os.remove(video_path)
        else:
            # someting is wrong
            await user.change_load_status(False, session)
            await session.commit()
            await message.answer(
                text = ru_strs.wait_link_error
            )

        # finish all states
        await state.finish()
        await state.reset_data()
