import asyncio
from datetime import datetime
from loader import reminder_col, bot
from services.gpt_service import get_reminder_text


async def check_and_send_reminders():
    """
    Проверяет базу данных на наличие напоминаний, которые нужно отправить.
    """
    while True:
        now = datetime.now()
        # Находим напоминания, время которых уже наступило
        reminders = reminder_col.find({
            "reminder_datetime": {"$lte": now.isoformat()}
        })

        async for reminder in reminders:
            user_id = reminder["user_id"]
            text = reminder["reminder_text"]
            reminder_text = await get_reminder_text(text)
            # Отправляем напоминание пользователю
            await bot.send_message(chat_id=user_id, text=reminder_text)

            # Удаляем напоминание из базы данных
            await reminder_col.delete_one({"_id": reminder["_id"]})

        # Ждем некоторое время перед следующей проверкой
        await asyncio.sleep(20)  # Проверяем каждую минуту
