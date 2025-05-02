"""Общие обработчики: /start, /help и др."""

from aiogram import Router, types, F
from aiogram.filters import Command
from services.admin_api import AdminAPI

router = Router()

@router.message(Command("admins"))
async def get_admins_handler(message: types.Message):
    try:
        admins = await AdminAPI.get_admins()
        print(f"[DEBUG] Admins from API: {admins}")
        await message.answer("Проверка выполнена.")
    except Exception as e:
        print(f"[ERROR] Ошибка при получении админов: {e}")
        await message.answer("Ошибка при проверке. См. логи.")
