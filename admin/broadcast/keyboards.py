from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from common.keyboards import build_back_button, build_back_to_home_page_button
from common.lang_dicts import BUTTONS
import models


def build_broadcast_keyboard(lang: models.Language = models.Language.ARABIC):
    keyboard = [
        [
            InlineKeyboardButton(
                text=BUTTONS[lang]["everyone"],
                callback_data="everyone",
            ),
            InlineKeyboardButton(
                text=BUTTONS[lang]["specific_users"],
                callback_data="specific_users",
            ),
        ],
        [
            InlineKeyboardButton(
                text=BUTTONS[lang]["all_users"],
                callback_data="all_users",
            ),
            InlineKeyboardButton(
                text=BUTTONS[lang]["all_admins"],
                callback_data="all_admins",
            ),
        ],
        [
            InlineKeyboardButton(
                text=BUTTONS[lang]["channel_or_group"],
                callback_data="channel_or_group",
            ),
        ],
        build_back_button("back_to_the_message", lang=lang),
        build_back_to_home_page_button(lang=lang, is_admin=True)[0],
    ]
    return InlineKeyboardMarkup(keyboard)


