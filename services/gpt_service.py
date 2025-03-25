from datetime import datetime
from pprint import pprint

from loader import yandex_gpt
from utils.gpt_queries import system_get_meta_prompt, system_get_delete_good_query, system_create_reminder_query, \
    system_get_reminders_prompt, get_reminder_text_query, get_reminder_change_query_prompt


async def get_task_meta(text):
    query = [
        {
            "role": "system",
            "text": system_get_meta_prompt
        },
        {
            "role": "user",
            "text": text
        }
    ]

    gpt_result = await send_query(query)
    print(gpt_result)

    return gpt_result.strip("```")


async def get_delete_good_ids(good_list_str: str, delete_list_str: str):
    query = [
        {
            "role": "system",
            "text": system_get_delete_good_query
        },
        {
            "role": "user",
            "text": f"Весь список: {good_list_str}\nНеобходимо удалить: {delete_list_str}"
        }
    ]
    gpt_result = await send_query(query)
    print(gpt_result)
    return gpt_result.strip("```")


async def create_reminder_meta(reminder_text):
    current_datetime_str = datetime.now().strftime("%d.%m.%Y %H:%M:%S %A")
    system_prompt = system_create_reminder_query.replace("{{current_datetime}}", current_datetime_str)
    query = [
        {
            "role": "system",
            "text": system_prompt
        },
        {
            "role": "user",
            "text": f"{reminder_text}"
        }
    ]
    gpt_result = await send_query(query)
    print(gpt_result)
    return gpt_result.strip("```")

async def get_reminders_gpt(usr_query, reminders_array):
    current_datetime_str = datetime.now().strftime("%d.%m.%Y %H:%M:%S %A")
    query = [
        {
            "role": "system",
            "text": system_get_reminders_prompt
        },
        {
            "role": "user",
            "text": f"Запрос пользователя: {usr_query}\nСписок напоминаний: {reminders_array},\nтекущая дата: {current_datetime_str}"
        }
    ]
    gpt_result = await send_query(query)
    print(gpt_result)
    return gpt_result.strip("`")


async def get_reminder_text(usr_query):
    query = [
        {
            "role": "system",
            "text": get_reminder_text_query
        },
        {
            "role": "user",
            "text": usr_query
        }
    ]
    return await send_query(query)


async def get_reminder_change_query(request, reminders):
    current_datetime_str = datetime.now().strftime("%d.%m.%Y %H:%M:%S %A")
    query = [
        {
            "role": "system",
            "text": get_reminder_change_query_prompt
        },
        {
            "role": "user",
            "text": f"Текст запроса: {request}, Массив напоминаний: {reminders}\n\n "
                    f"Текущая дата и время: {current_datetime_str}"
        }
    ]
    gpt_result = await send_query(query)
    print(gpt_result)
    return gpt_result.strip("```")


async def send_query(query):
    result = await yandex_gpt.run(query)
    return result[0].text
