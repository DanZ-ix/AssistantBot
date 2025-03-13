from loader import buy_list


async def get_goods_list_str():
    good_list = await get_goods_list()
    return ", ".join(good_list)


# Функция для получения всех элементов в виде массива строк
async def get_goods_list():
    goods_list = []

    # Извлекаем все документы из коллекции
    cursor = buy_list.find({})

    # Перебираем результаты и добавляем значения в список
    async for document in cursor:
        if "good" in document:  # Проверяем, что поле "good" существует
            goods_list.append(document["good"])

    return goods_list
