from loader import buy_list
from services.goods_service import get_goods_list_str, get_goods_documents, find_and_delete_objects, divide_list_goods
from services.gpt_service import send_query, get_delete_good_ids
from services.notes_service import add_note


async def process_gpt_results(meta_dict_list):
    gpt_functions = {
        "save_note": save_note,
        "general_question": general_question,
        "add_good_to_list": add_good_to_list,
        "get_buy_list": get_buy_list,
        "delete_goods": delete_goods
    }

    return_str = ""
    for meta_dict in meta_dict_list:
        return_str += await gpt_functions[meta_dict["action"]](meta_dict["result"]) + "\n\n"
    return return_str


async def save_note(text):
    add_note(text)
    return "Заметка добавлена:\n" + text


async def general_question(prompt):
    response = await send_query(prompt)
    return f"Ответ: ({prompt})\n" + response


async def add_good_to_list(query):
    await buy_list.insert_many(query)
    ret_str = "Добавлены в список покупок:\n"
    for i in query:
        ret_str += f"* {i['good']}\n"
    return ret_str


async def get_buy_list(_):
    return "Список покупок: " + await get_goods_list_str()


async def delete_goods(query):
    doc_list = await get_goods_documents()
    delete_ids = await get_delete_good_ids(str(doc_list), str(query))
    res = await find_and_delete_objects(delete_ids)
    return "Удалены продукты:" + divide_list_goods(res)

