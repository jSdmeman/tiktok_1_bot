from aiogram import executor
from aiogram import types
import os
import fcntl

from config import bot, dp, redis_storage
from database.base import Base
import database
import handlers
import strings


# before start
async def on_startup(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "🚀 запуск бота"),
        types.BotCommand("load", "💾 скачать видео"),
        types.BotCommand("info", "❓ база")
    ])


# before shutdown
async def on_shutdown(dp):
    await redis_storage.close()
    await redis_storage.wait_closed()
    await bot.session.close()


if __name__ == "__main__":
    # блок от повторного запуска
    fp = open(os.path.realpath(__file__), 'r')
    try:
        fcntl.flock(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except:
        exit(0)

    # run
    executor.start_polling(
        dp,
        on_startup = on_startup,
        on_shutdown = on_shutdown,
        skip_updates = True
    )
