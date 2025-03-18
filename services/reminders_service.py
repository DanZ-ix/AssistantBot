from datetime import datetime

from loader import reminder_col

async def save_reminder_to_db(reminder_data):
    """
    Сохраняет напоминание в MongoDB.

    :param user_id: ID пользователя Telegram.
    :param text: Текст напоминания.
    :param reminder_datetime: Дата и время напоминания.
    """
    await reminder_col.insert_one(reminder_data)


async def get_reminders_by_user_id(user_id: int):
    """
    Получает все напоминания для указанного user_id.

    :param user_id: ID пользователя Telegram.
    :return: Список напоминаний в формате словарей.
    """
    # Находим все напоминания для данного user_id
    reminders = await reminder_col.find({"user_id": user_id}).to_list(None)

    return reminders
