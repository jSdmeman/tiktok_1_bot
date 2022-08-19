from aiogram import types
from aiogram.dispatcher import FSMContext

from config import dp


@dp.message_handler(state='*')
async def unknown_message(message: types.Message, state: FSMContext):
    # delete unknown message
    try:
        await message.delete()
    except Exception as ERROR:
        print(ERROR)


@dp.callback_query_handler(state='*')
async def unknown_message(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
