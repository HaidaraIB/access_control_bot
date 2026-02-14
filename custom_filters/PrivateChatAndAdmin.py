from telegram import Update
from telegram.ext.filters import BaseFilter
from custom_filters import PrivateChat, Admin


class PrivateChatAndAdmin(BaseFilter):
    def filter(self, update: Update):
        return PrivateChat().filter(update) and Admin().filter(update)
