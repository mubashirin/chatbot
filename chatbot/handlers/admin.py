"""Обработчики команд администраторов."""

from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command, Filter
from services.admin_api import AdminAPI
from services.chat_manager import ChatManager
from aiogram.types import CallbackQuery

router = Router()
chat_manager = ChatManager()

async def is_admin(user_id: int) -> bool:
    admins = await AdminAPI.get_admins()
    return user_id in admins

@router.message(CommandStart())
async def admin_start_handler(message: types.Message):
    if await is_admin(message.from_user.id):
        await message.answer("Вы администратор. Используйте /chats для просмотра активных чатов.")
    else:
        await message.answer("Добро пожаловать!")

@router.message(Command("chats"))
async def admin_chats_handler(message: types.Message):
    if not await is_admin(message.from_user.id):
        await message.answer("Нет доступа.")
        return
    chats = chat_manager.get_active_chats(message.from_user.id)
    if not chats:
        await message.answer("У вас нет активных чатов.")
        return
    text = "Ваши активные чаты:\n" + "\n".join([f"Чат #{c.chat_id} с пользователем {c.user_id}" for c in chats])
    await message.answer(text)

@router.message(Command("reply"))
async def admin_reply_handler(message: types.Message):
    if not await is_admin(message.from_user.id):
        return
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("Используйте: /reply <chat_id> <текст>")
        return
    try:
        chat_id = int(args[1])
    except ValueError:
        await message.answer("Некорректный chat_id")
        return
    text = args[2]
    chat = chat_manager.storage.get_chat(chat_id)
    if not chat or chat.admin_id != message.from_user.id or not chat.is_active or not getattr(chat, 'accepted', False):
        await message.answer("Чат не найден, не принадлежит вам или не принят.")
        return
    # Сохраняем сообщение
    chat_manager.add_message(chat_id, message.from_user.id, text)
    # Отправляем клиенту
    from aiogram import Bot
    from config.config import API_TOKEN
    bot = Bot(token=API_TOKEN)
    await bot.send_message(chat.user_id, f"Админ: {text}")
    await message.answer("Ответ отправлен клиенту.")

@router.callback_query(F.data.startswith("decline_chat:"))
async def decline_chat_handler(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("Нет доступа.", show_alert=True)
        return
    chat_id = int(callback.data.split(":")[1])
    chat = chat_manager.storage.get_chat(chat_id)
    if not chat or chat.admin_id != callback.from_user.id or not chat.is_active:
        await callback.answer("Чат не найден или не принадлежит вам.", show_alert=True)
        return
    chat.is_active = False
    chat_manager.storage.db.commit()
    # Уведомить клиента
    from aiogram import Bot
    from config.config import API_TOKEN
    bot = Bot(token=API_TOKEN)
    try:
        await bot.send_message(chat.user_id, "Ваша беседа была отклонена администратором.")
    except Exception:
        pass
    await callback.message.edit_text(callback.message.text + "\n\n❌ Беседа отклонена.")
    await callback.answer("Беседа отклонена.", show_alert=True)

@router.callback_query(F.data.startswith("accept_chat:"))
async def accept_chat_handler(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("Нет доступа.", show_alert=True)
        return
    chat_id = int(callback.data.split(":")[1])
    chat = chat_manager.storage.get_chat(chat_id)
    if not chat or chat.admin_id != callback.from_user.id or not chat.is_active:
        await callback.answer("Чат не найден или не принадлежит вам.", show_alert=True)
        return
    chat.accepted = True
    chat_manager.storage.db.commit()
    # Уведомить клиента
    from aiogram import Bot
    from config.config import API_TOKEN
    bot = Bot(token=API_TOKEN)
    try:
        await bot.send_message(chat.user_id, "Вашу беседу принял администратор. Ожидайте ответа.")
    except Exception:
        pass
    await callback.message.edit_text(callback.message.text + "\n\n✅ Беседа принята.")
    await callback.answer("Беседа принята.", show_alert=True)

@router.callback_query(F.data.startswith("end_chat:"))
async def end_chat_handler(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("Нет доступа.", show_alert=True)
        return
    chat_id = int(callback.data.split(":")[1])
    chat = chat_manager.storage.get_chat(chat_id)
    if not chat or chat.admin_id != callback.from_user.id or not chat.is_active:
        await callback.answer("Чат не найден или не принадлежит вам.", show_alert=True)
        return
    chat.is_active = False
    chat_manager.storage.db.commit()
    # Уведомить клиента
    from aiogram import Bot
    from config.config import API_TOKEN
    bot = Bot(token=API_TOKEN)
    try:
        await bot.send_message(chat.user_id, "Беседа завершена администратором.")
    except Exception:
        pass
    await callback.message.edit_text(callback.message.text + "\n\n❌ Беседа завершена.")
    await callback.answer("Беседа завершена.", show_alert=True)

@router.callback_query(F.data.startswith("transfer_chat:"))
async def transfer_chat_handler(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("Нет доступа.", show_alert=True)
        return
    await callback.answer("Заглушка: переправить чат другому админу.", show_alert=True)

class IsAdmin(Filter):
    async def __call__(self, message: types.Message) -> bool:
        from services.admin_api import AdminAPI
        return message.from_user.id in await AdminAPI.get_admins()

@router.message(IsAdmin())
async def admin_text_handler(message: types.Message):
    print(f"[DEBUG] admin_text_handler: user_id={message.from_user.id}, text={message.text}")
    if not await is_admin(message.from_user.id):
        return
    from db.models import Chat
    chat = chat_manager.storage.db.query(Chat).filter_by(admin_id=message.from_user.id, is_active=True, accepted=True).order_by(Chat.chat_id.desc()).first()
    print(f"[DEBUG] Найден чат: {chat}")
    if not chat:
        await message.answer("Нет активных принятых чатов. Используйте /chats для просмотра.")
        return
    # Сохраняем сообщение
    chat_manager.add_message(chat.chat_id, message.from_user.id, message.text)
    # Отправляем клиенту
    from aiogram import Bot
    from config.config import API_TOKEN
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    bot = Bot(token=API_TOKEN)
    print(f"[DEBUG] Отправляю клиенту {chat.user_id}: {message.text}")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔚 Завершить беседу", callback_data="end_chat_by_client")]
    ])
    await bot.send_message(chat.user_id, f"Админ: {message.text}", reply_markup=kb)
