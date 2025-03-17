from bson import ObjectId

from loader import buy_list


def divide_list_goods(good_document_list):
    goods_list = []
    for doc in good_document_list:
        if "good" in doc:  # Проверяем, что поле "good" существует
            goods_list.append(doc["good"])
    return "\n* " + "\n* ".join(goods_list)


async def get_goods_list_str():
    good_list = await get_goods_list()
    return "\n* " + "\n* ".join(good_list)


# Функция для получения всех элементов в виде массива строк
async def get_goods_list():
    doc_list = await get_goods_documents()
    goods_list = []
    for doc in doc_list:
        if "good" in doc:  # Проверяем, что поле "good" существует
            goods_list.append(doc["good"])
    return goods_list


async def get_goods_documents():
    document_list = []

    # Извлекаем все документы из коллекции
    cursor = buy_list.find({})

    # Перебираем результаты и добавляем значения в список
    async for document in cursor:
        document_list.append(document)
    return document_list


async def find_and_delete_objects(ids_string):
    # Шаг 1: Найти документы перед удалением
    ids = parse_object_ids(ids_string)
    filter_query = {"_id": {"$in": ids}}
    deleted_objects = await buy_list.find(filter_query).to_list(length=None)  # Получаем все найденные документы

    # Шаг 2: Удалить документы
    await buy_list.delete_many(filter_query)
    # Возвращаем удаленные документы
    return deleted_objects


def parse_object_ids(string):
    # Удаляем квадратные скобки и префиксы/суффиксы ObjectId
    cleaned_string = string.replace("[", "").replace("]", "").replace("ObjectId(", "").replace(")", "")
    # Разделяем строку по запятым
    id_strings = [s.strip().strip("'") for s in cleaned_string.split(",")]
    # Преобразуем каждую строку в ObjectId
    return [ObjectId(id_str) for id_str in id_strings]
