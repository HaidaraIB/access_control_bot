from telegram import Update
from telegram.ext.filters import UpdateFilter
from Config import Config


class Owner(UpdateFilter):
    def filter(self, update: Update):
        return update.effective_user and update.effective_user.id == Config.OWNER_ID

