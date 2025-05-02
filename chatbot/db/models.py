"""Модели данных: User, Admin, Chat, Message."""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    chats = relationship('Chat', back_populates='user')

class Admin(Base):
    __tablename__ = 'admins'
    admin_id = Column(Integer, primary_key=True)
    username = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    chats = relationship('Chat', back_populates='admin')

class Chat(Base):
    __tablename__ = 'chats'
    chat_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    admin_id = Column(Integer, ForeignKey('admins.admin_id'), nullable=True)
    is_active = Column(Boolean, default=True)
    accepted = Column(Boolean, default=False)
    user = relationship('User', back_populates='chats')
    admin = relationship('Admin', back_populates='chats')
    messages = relationship('Message', back_populates='chat', cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = 'messages'
    message_id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chats.chat_id'))
    sender_id = Column(Integer)
    text = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    chat = relationship('Chat', back_populates='messages')
