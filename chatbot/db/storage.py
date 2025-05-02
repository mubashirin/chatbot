"""Интерфейс хранилища данных."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from db.models import Base, User, Admin, Chat, Message

DATABASE_URL = "sqlite:///chatbot.sqlite3"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))

# Создание таблиц
Base.metadata.create_all(bind=engine)

# CRUD-утилиты
class Storage:
    def __init__(self):
        self.db = SessionLocal()

    # User
    def get_user(self, user_id: int):
        return self.db.query(User).filter_by(user_id=user_id).first()

    def create_user(self, user_id: int, **kwargs):
        user = User(user_id=user_id, **kwargs)
        self.db.add(user)
        self.db.commit()
        return user

    # Admin
    def get_admin(self, admin_id: int):
        return self.db.query(Admin).filter_by(admin_id=admin_id).first()

    def create_admin(self, admin_id: int, **kwargs):
        admin = Admin(admin_id=admin_id, **kwargs)
        self.db.add(admin)
        self.db.commit()
        return admin

    # Chat
    def get_chat(self, chat_id: int):
        return self.db.query(Chat).filter_by(chat_id=chat_id).first()

    def create_chat(self, user_id: int, admin_id: int = None):
        chat = Chat(user_id=user_id, admin_id=admin_id)
        self.db.add(chat)
        self.db.commit()
        return chat

    # Message
    def add_message(self, chat_id: int, sender_id: int, text: str):
        msg = Message(chat_id=chat_id, sender_id=sender_id, text=text)
        self.db.add(msg)
        self.db.commit()
        return msg

    def get_messages(self, chat_id: int):
        return self.db.query(Message).filter_by(chat_id=chat_id).order_by(Message.timestamp).all()

    def close(self):
        self.db.close()
