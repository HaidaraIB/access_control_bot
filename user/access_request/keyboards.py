from telegram import InlineKeyboardButton
from common.lang_dicts import BUTTONS
import models


def build_access_request_keyboard(
    req_id: int, lang: models.Language = models.Language.ARABIC
):
    keyboard = [
        [
            InlineKeyboardButton(
                text=BUTTONS[lang]["access_request_approve"],
                callback_data=f"access_approve_{req_id}",
            ),
            InlineKeyboardButton(
                text=BUTTONS[lang]["access_request_reject"],
                callback_data=f"access_reject_{req_id}",
            ),
        ],
    ]
    return keyboard
