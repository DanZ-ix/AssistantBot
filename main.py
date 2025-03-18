
from aiogram import types
from handlers import dp
import asyncio

from utils.scheduled import check_and_send_reminders


async def set_commands(bot):
    await bot.set_my_commands([
        types.BotCommand(command="gen_links", description="Сгенерировать ссылки на токен")
    ])


async def main():
    from loader import bot
    # await set_commands(bot)
    # await mongo_conn.connect_server()
    await asyncio.gather(dp.start_polling(bot),
                         check_and_send_reminders())


if __name__ == '__main__':
    #asyncio.run(test())
    asyncio.run(main())