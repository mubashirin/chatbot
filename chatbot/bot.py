"""Точка входа для запуска бота."""

import asyncio
from aiogram import Bot, Dispatcher
from config.config import API_TOKEN
import config.logging
from handlers import admin, client, common

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def setup_routers():
    dp.include_router(admin.router)
    dp.include_router(client.router)
    dp.include_router(common.router)

async def main():
    setup_routers()
    print("Бот запущен. Ожидание событий...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
