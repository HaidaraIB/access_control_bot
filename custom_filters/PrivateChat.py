from telegram import Update, Chat
from telegram.ext.filters import BaseFilter


class PrivateChat(BaseFilter):
    def filter(self, update: Update):
        return update.effective_chat and update.effective_chat.type == Chat.PRIVATE
