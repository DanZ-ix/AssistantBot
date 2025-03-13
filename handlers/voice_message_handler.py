import json
import logging
import asyncio
import requests

from aiogram import types, F
from aiogram.filters import Command

from loader import dp, bot, yandex_api_token, buy_list
from services.gpt_service import get_task_meta, send_query
from services.goods_service import get_goods_list, get_goods_list_str
from services.notes_service import add_note
from utils.states import States
from utils.funcs import check_admin
from services.voice_recognition_service import recognize_audio


async def process_message_text(text: str, message: types.Message):
    text_meta = await get_task_meta(text)
    if text_meta:
        meta_dict_list = json.loads(text_meta)
        adding_buy_list = []

        for meta_dict in meta_dict_list:
            if meta_dict["action"] == "save_note":
                add_note(meta_dict["parameters"]["note_text"])
                await message.answer("Заметка добавлена")
            elif meta_dict["action"] == "general_question":
                result = meta_dict["parameters"]["response"]
                await message.answer("Ответ: " + result)
            elif meta_dict["action"] == "add_good_to_list":
                query = meta_dict["parameters"]["insert_query"]
                await buy_list.insert_one(query)
                adding_buy_list.append(query["good"])
            elif meta_dict["action"] == "get_buy_list":
                await message.answer("Список покупок: " + await get_goods_list_str())
        if len(adding_buy_list) > 0:
            await message.answer("Добавлены покупки: " + await get_goods_list_str())


@dp.message(Command("buy_list"))
async def get_buy_list(message: types.Message):
    if not check_admin(message.from_user.id):
        return
    try:
        await message.answer("Список покупок: " + await get_goods_list_str())
    except Exception as e:
        print(e)


@dp.message(F.text)
async def handle_text_message(message: types.Message):
    if not check_admin(message.from_user.id):
        return
    if message.text.startswith("/"):
        return
    try:
        await process_message_text(message.text, message)
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
        await process_message_text(audio_text, message)
    except Exception as e:
        logging.error(e)
        print(e)
        await message.reply(f"Произошла ошибка: {str(e)}")
