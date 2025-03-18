from datetime import datetime

from loader import admin_list


def check_admin(id: int) -> bool:
    return str(id) in admin_list


def convert_to_human_readable_with_month_name(date_str):
    """
    Преобразует строку с датой в формате ISO 8601 в человекочитаемый формат,
    где месяц пишется словом.

    :param date_str: Строка с датой в формате "YYYY-MM-DDTHH:MM:SS".
    :return: Человекочитаемая строка с датой и временем.
    """
    # Парсим строку в объект datetime
    dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")

    # Форматируем дату и время
    day = dt.strftime("%d")  # День месяца (01–31)
    year = dt.strftime("%Y")  # Год (четырехзначный)
    time = dt.strftime("%H:%M:%S")  # Время

    # Получаем название месяца словом
    months = [
        "января", "февраля", "марта", "апреля", "мая", "июня",
        "июля", "августа", "сентября", "октября", "ноября", "декабря"
    ]
    month_name = months[dt.month - 1]  # Месяц начинается с 1, а индекс списка — с 0

    # Формируем человекочитаемую строку
    human_readable = f"{day} {month_name} {year} {time}"

    return human_readable
