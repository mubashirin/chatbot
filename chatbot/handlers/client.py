"""Обработчики сообщений клиентов."""

from aiogram import Router, types
from aiogram.filters import CommandStart, Filter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.chat_manager import ChatManager
from db.storage import Storage
from db.models import User, Chat

router = Router()
chat_manager = ChatManager()

class NotAdmin(Filter):
    async def __call__(self, message: types.Message) -> bool:
        from services.admin_api import AdminAPI
        return message.from_user.id not in await AdminAPI.get_admins()

@router.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("Добро пожаловать! Ожидайте ответа администратора.")

@router.callback_query(lambda c: c.data == "end_chat_by_client")
async def end_chat_by_client_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    storage = Storage()
    chat = storage.db.query(Chat).filter_by(user_id=user_id, is_active=True).first()
    if not chat:
        await callback.answer("У вас нет активных бесед.", show_alert=True)
        return
    
    chat.is_active = False
    storage.db.commit()
    
    # Уведомить админа
    from aiogram import Bot
    from config.config import API_TOKEN
    bot = Bot(token=API_TOKEN)
    try:
        await bot.send_message(chat.admin_id, f"❌ Пользователь завершил беседу #{chat.chat_id}")
    except Exception:
        pass
    
    await callback.message.edit_text("✅ Вы завершили беседу с администратором.")
    await callback.answer("Беседа завершена.", show_alert=True)

@router.message(NotAdmin())
async def client_message_handler(message: types.Message):
    print(f"[DEBUG] client_message_handler: user_id={message.from_user.id}, text={message.text}")
    user_id = message.from_user.id
    storage = Storage()
    # Создать пользователя, если нет
    if not storage.get_user(user_id):
        storage.create_user(user_id, username=message.from_user.username, first_name=message.from_user.first_name, last_name=message.from_user.last_name)
    # Назначить админа
    admin_id = await chat_manager.assign_admin()
    if not admin_id:
        await message.answer("Нет свободных администраторов. Попробуйте позже.")
        return
    # Создать чат, если нет
    chat = storage.db.query(Chat).filter_by(user_id=user_id, is_active=True).first()
    if not chat:
        chat = chat_manager.start_chat(user_id, admin_id)
    # Если чат не принят — каждое сообщение отправлять админу с кнопками
    if not getattr(chat, 'accepted', False):
        chat_manager.add_message(chat.chat_id, user_id, message.text)
        await message.answer("Ожидайте, пока администратор примет вашу беседу.")
        if chat.admin_id:
            from aiogram import Bot
            from config.config import API_TOKEN
            bot = Bot(token=API_TOKEN)
            user = storage.get_user(user_id)
            if user:
                name = user.first_name or ""
                if user.last_name:
                    name += f" {user.last_name}"
                if user.username:
                    name = f"@{user.username} ({name.strip()})" if name.strip() else f"@{user.username}"
                name = name.strip() or str(user_id)
            else:
                name = str(user_id)
            text = f"📩 Новое сообщение от пользователя {name} в чате #{chat.chat_id}:\n\n{message.text}"
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_chat:{chat.chat_id}"),
                    InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline_chat:{chat.chat_id}")
                ]
            ])
            print(f"[DEBUG] Отправляю админу {chat.admin_id} (type: {type(chat.admin_id)}): {text}")
            await bot.send_message(chat.admin_id, text, reply_markup=kb)
        return
    # Сохранить сообщение (если чат уже принят)
    chat_manager.add_message(chat.chat_id, user_id, message.text)
    await message.answer("✅ Ваше сообщение отправлено администратору.")
    # Уведомить назначенного админа (без кнопок)
    if chat.admin_id:
        from aiogram import Bot
        from config.config import API_TOKEN
        bot = Bot(token=API_TOKEN)
        print(f"[DEBUG] Отправляю админу {chat.admin_id} (type: {type(chat.admin_id)}): {message.text}")
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔚 Завершить беседу", callback_data=f"end_chat:{chat.chat_id}"),
                InlineKeyboardButton(text="🔄 Переправить", callback_data=f"transfer_chat:{chat.chat_id}")
            ]
        ])
        await bot.send_message(chat.admin_id, f"📩 Новое сообщение #{chat.chat_id}:\n\n{message.text}", reply_markup=kb)
