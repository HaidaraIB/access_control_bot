from telegram import Update
from telegram.ext.filters import UpdateFilter
import models


class Admin(UpdateFilter):
    def filter(self, update: Update):
        with models.session_scope() as s:
            user = s.get(
                models.User,
                update.effective_user.id,
            )
            return user and user.is_admin
