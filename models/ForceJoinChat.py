import sqlalchemy as sa
from models.DB import Base
from datetime import datetime


class ForceJoinChat(Base):
    __tablename__ = "force_join_chats"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    chat_id = sa.Column(sa.BigInteger, unique=True, nullable=False)
    chat_link = sa.Column(sa.String, nullable=False)
    chat_title = sa.Column(sa.String, nullable=True)

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

    def __str__(self):
        return (
            f"Chat ID: <code>{self.chat_id}</code>\n"
            f"Chat Link: {self.chat_link}\n"
            f"Chat Title: <b>{self.chat_title}</b>"
        )

    def __repr__(self):
        return f"ForceJoinChat(id={self.id}, chat_id={self.chat_id}, chat_link={self.chat_link})"
