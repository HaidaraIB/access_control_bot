from telegram import InlineKeyboardButton
from common.lang_dicts import BUTTONS, TEXTS
from common.keyboards import build_keyboard
import models


def build_access_request_keyboard(
    req_id: int, lang: models.Language = models.Language.ARABIC
):
    """Approve/Reject buttons for one access request (BUTTONS labels)."""
    return [
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


def build_access_requests_settings_keyboard(
    lang: models.Language = models.Language.ARABIC,
):
    """Four buttons: request pending, history, back, back to home (all from BUTTONS)."""
    return [
        [
            InlineKeyboardButton(
                text=BUTTONS[lang]["request_pending_access_request"],
                callback_data="request_pending_access_request",
            ),
        ],
        [
            InlineKeyboardButton(
                text=BUTTONS[lang]["access_request_history"],
                callback_data="access_request_history",
            ),
        ],
    ]


def build_access_request_history_keyboard(
    access_requests: list,
    lang: models.Language = models.Language.ARABIC,
):
    """Last 20 access requests as buttons + back + back to home. Uses TEXTS for status labels."""
    status_key = {
        models.AccessRequestStatus.PENDING: "status_pending",
        models.AccessRequestStatus.APPROVED: "status_approved",
        models.AccessRequestStatus.REJECTED: "status_rejected",
    }
    if not access_requests:
        keyboard = []
    else:
        texts = []
        for a in access_requests:
            key = status_key.get(a.status, "status_pending")
            texts.append(f"#{a.id} ({TEXTS[lang][key]})")
        buttons_data = [f"access_request_id_{a.id}" for a in access_requests]
        keyboard = build_keyboard(columns=2, texts=texts, buttons_data=buttons_data)
    return keyboard
