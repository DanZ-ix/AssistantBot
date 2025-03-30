import json
from datetime import datetime

from loader import buy_list
from services.goods_service import get_goods_list_str, get_goods_documents, find_and_delete_objects, divide_list_goods
from services.gpt_service import send_query, get_delete_good_ids, create_reminder_meta, get_reminders_gpt, \
    get_reminder_change_query, get_notes_gpt
from services.notes_service import add_note, save_note_mongo, get_notes_objects, get_notes_by_objectids, get_notes_str
from services.reminders_service import save_reminder_to_db, get_reminders_by_user_id, format_reminders, \
    get_reminders_by_object_ids, process_reminder_operation
from utils.funcs import convert_to_human_readable_with_month_name


async def process_gpt_results(meta_dict_list, user_id):
    gpt_functions = {
        save_note.__name__          : save_note,
        get_notes.__name__          : get_notes,
        general_question.__name__   : general_question,
        add_good_to_list.__name__   : add_good_to_list,
        get_buy_list.__name__       : get_buy_list,
        delete_goods.__name__       : delete_goods,
        add_reminder.__name__       : add_reminder,
        change_reminder.__name__    : change_reminder,
        get_reminders.__name__      : get_reminders,
        unknown_request.__name__    : unknown_request
    }

    return_str = ""
    for meta_dict in meta_dict_list:
        return_str += await gpt_functions[meta_dict["action"]](meta_dict["result"], str(user_id)) + "\n\n"
    return return_str


async def save_note(text, user_id):
    await save_note_mongo(text, user_id)
    #add_note(text)
    return "Заметка добавлена:\n" + text


async def get_notes(text, user_id):
    notes_list_full = await get_notes_objects(user_id)
    notes_obj_ids = await get_notes_gpt(text, notes_list_full)
    notes_list = await get_notes_by_objectids(notes_obj_ids)
    return get_notes_str(notes_list)


async def general_question(prompt, _):
    response = await send_query(prompt)
    return f"Ответ: ({prompt})\n" + response


async def add_good_to_list(query, user_id):
    for item in query:
        item["user_id"] = str(user_id)
    await buy_list.insert_many(query)
    ret_str = "Добавлены в список покупок:\n"
    for i in query:
        ret_str += f"* {i['good']}\n"
    return ret_str


async def get_buy_list(_, user_id):
    return "Список покупок: " + await get_goods_list_str(user_id)


async def delete_goods(query, user_id):
    doc_list = await get_goods_documents(user_id)
    delete_ids = await get_delete_good_ids(str(doc_list), str(query))
    if delete_ids.strip() == "[]":
        return "Продукты не удалены"
    res = await find_and_delete_objects(delete_ids)
    return "Удалены продукты:" + divide_list_goods(res)


async def add_reminder(reminder, user_id):
    reminder_json = await create_reminder_meta(reminder)
    reminder_dict = json.loads(reminder_json)
    reminder_dict["user_id"] = str(user_id)
    await save_reminder_to_db(reminder_dict)
    return (f"Добавлена заметка на {convert_to_human_readable_with_month_name(reminder_dict['reminder_datetime'])}\n"
            f"Текст заметки: {reminder_dict['reminder_text']}")


async def get_reminders(reminder_prompt, user_id):
    reminders = await get_reminders_by_user_id(user_id)
    if len(reminders) == 0:
        return "Упоминания не найдены"
    if reminder_prompt is None:
        return format_reminders(str(reminders))

    object_ids = await get_reminders_gpt(reminder_prompt, str(reminders))
    if object_ids == '[]':
        return "Упоминания не найдены"
    filtered_reminders = await get_reminders_by_object_ids(object_ids)
    if filtered_reminders:
        return format_reminders(str(filtered_reminders))
    return "Упоминания не найдены"


async def change_reminder(change_request, user_id):
    reminder_list = await get_reminders_by_user_id(user_id)
    reminder_change_query = await get_reminder_change_query(change_request, reminder_list)
    return await process_reminder_operation(reminder_change_query)


async def unknown_request(request, _):
    return "Для данного запроса пока не предусмотрен функционал " + request
