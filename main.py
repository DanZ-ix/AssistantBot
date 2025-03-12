
from aiogram import types
from handlers import dp
import asyncio
from test import test
from services.notes_service import add_note


async def set_commands(bot):
    await bot.set_my_commands([
        types.BotCommand(command="gen_links", description="Сгенерировать ссылки на токен"),
        types.BotCommand(command="list_acc", description="Список отслеживаемых аккаунтов ТГ"),
        types.BotCommand(command="add_acc", description="Добавить аккаунт ТГ"),
        types.BotCommand(command="delete_acc", description="Удалить аккаунт ТГ")
    ])


async def main():
    from loader import bot
    # await set_commands(bot)
    # await mongo_conn.connect_server()
    await asyncio.gather(dp.start_polling(bot))


if __name__ == '__main__':
    #asyncio.run(test())
    asyncio.run(main())