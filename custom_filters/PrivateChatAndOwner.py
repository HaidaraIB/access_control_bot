from telegram import Update
from telegram.ext.filters import BaseFilter
from custom_filters import PrivateChat, Owner


class PrivateChatAndOwner(BaseFilter):
    def filter(self, update: Update):
        return PrivateChat().filter(update) and Owner().filter(update)

