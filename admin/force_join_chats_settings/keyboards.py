from telegram import InlineKeyboardButton
from common.lang_dicts import BUTTONS
import models


def build_force_join_chats_keyboard(lang: models.Language = models.Language.ARABIC):
    keyboard = [
        [
            InlineKeyboardButton(
                text=BUTTONS[lang]["add_force_join_chat"],
                callback_data="add_force_join_chat",
            ),
            InlineKeyboardButton(
                text=BUTTONS[lang]["remove_force_join_chat"],
                callback_data="remove_force_join_chat",
            ),
        ],
        [
            InlineKeyboardButton(
                text=BUTTONS[lang]["show_force_join_chats"],
                callback_data="show_force_join_chats",
            )
        ],
    ]
    return keyboard
