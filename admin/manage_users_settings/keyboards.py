from telegram import InlineKeyboardButton
from common.lang_dicts import BUTTONS
import models


def build_manage_users_settings_keyboard(lang: models.Language = models.Language.ARABIC):
    keyboard = [
        [
            InlineKeyboardButton(
                text=BUTTONS[lang]["export_users_to_excel"],
                callback_data="export_users_to_excel",
            )
        ],
    ]
    return keyboard

