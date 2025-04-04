import json
import logging


from aiogram import types, F
from aiogram.filters import Command

from loader import dp, bot
from services.gpt_service import get_task_meta
from services.goods_service import get_goods_list_str
from utils.gpt_functions import process_gpt_results
from utils.states import States
from utils.funcs import check_admin
from services.voice_recognition_service import recognize_audio


async def process_message_text(text: str, user_id) -> str:
    text_meta = await get_task_meta(text)
    if text_meta:
        meta_dict_list = json.loads(text_meta)
        return await process_gpt_results(meta_dict_list, user_id)


@dp.message(Command("start"))
async def start_command(message: types.Message):
    if not check_admin(message.from_user.id):
        return




@dp.message(Command("buy_list"))
async def get_buy_list(message: types.Message):
    if not check_admin(message.from_user.id):
        return
    try:
        await message.answer("Список покупок: " + await get_goods_list_str(str(message.from_user.id)))
    except Exception as e:
        print(e)


@dp.message(F.text)
async def handle_text_message(message: types.Message):
    if not check_admin(message.from_user.id):
        return
    if message.text.startswith("/"):
        return
    try:
        await message.answer(await process_message_text(message.text, message.from_user.id))
    except Exception as e:
        logging.error(e)
        print(e)
        await message.reply(f"Произошла ошибка: {str(e)}")


@dp.message(F.voice)
async def handle_voice_message(message: types.Message):
    if not check_admin(message.from_user.id):
        return

    voice = message.voice
    file_id = voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    downloaded_file = await bot.download_file(file_path)

    try:
        audio_text = await recognize_audio(downloaded_file)
        await message.answer(await process_message_text(audio_text, message.from_user.id))
    except Exception as e:
        logging.error(e)
        print(e)
        await message.reply(f"Произошла ошибка: {str(e)}")
