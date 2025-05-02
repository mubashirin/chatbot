"""Управление чатами и состояниями."""

from db.storage import Storage
from services.admin_api import AdminAPI
from db.models import Chat, User, Admin, Message
from typing import Optional
import asyncio

class ChatManager:
    def __init__(self):
        self.storage = Storage()

    async def sync_admins(self):
        api_admins = await AdminAPI.get_admins()
        db_admins = {a.admin_id for a in self.storage.db.query(Admin).all()}
        # Добавить новых
        for admin_id in api_admins:
            if not self.storage.get_admin(admin_id):
                self.storage.create_admin(admin_id=admin_id)
        # Деактивировать отсутствующих
        for admin in self.storage.db.query(Admin).all():
            if admin.admin_id not in api_admins:
                admin.is_active = False
        self.storage.db.commit()

    async def assign_admin(self) -> Optional[int]:
        await self.sync_admins()
        # Выбрать свободного админа (наименьшее число активных чатов)
        admins = self.storage.db.query(Admin).filter_by(is_active=True).all()
        if not admins:
            return None
        admin = min(admins, key=lambda a: len(a.chats))
        return admin.admin_id

    def start_chat(self, user_id: int, admin_id: Optional[int] = None) -> Chat:
        chat = self.storage.create_chat(user_id=user_id, admin_id=admin_id)
        return chat

    def add_message(self, chat_id: int, sender_id: int, text: str) -> Message:
        return self.storage.add_message(chat_id, sender_id, text)

    def get_active_chats(self, admin_id: int):
        return self.storage.db.query(Chat).filter_by(admin_id=admin_id, is_active=True).all()

    def transfer_chat(self, chat_id: int, new_admin_id: int):
        chat = self.storage.get_chat(chat_id)
        if chat:
            chat.admin_id = new_admin_id
            self.storage.db.commit()
            return chat
        return None
