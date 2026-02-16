from telegram import InlineKeyboardButton
from common.lang_dicts import BUTTONS
import models


def build_submit_method_keyboard(lang: models.Language = models.Language.ARABIC):
    """Inline keyboard: Username+Password vs Order ID only."""
    keyboard = [
        [
            InlineKeyboardButton(
                text=BUTTONS[lang]["submit_username_password"],
                callback_data="submit_login_username_password",
            ),
        ],
        [
            InlineKeyboardButton(
                text=BUTTONS[lang]["submit_order_id_only"],
                callback_data="submit_login_order_id",
            ),
        ],
    ]
    return keyboard


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
