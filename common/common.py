from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from common.keyboards import build_request_buttons
import os
import models
import uuid
from datetime import datetime
from custom_filters import HasPermission
from models import Permission


def check_hidden_permission_requests_keyboard(context: ContextTypes.DEFAULT_TYPE, admin_id: int):
    if not HasPermission.check(admin_id, Permission.VIEW_IDS):
        reply_markup = ReplyKeyboardRemove()
    elif (
        not context.user_data.get("request_keyboard_hidden", None)
        or not context.user_data["request_keyboard_hidden"]
    ):
        context.user_data["request_keyboard_hidden"] = False
        request_buttons = build_request_buttons()
        reply_markup = ReplyKeyboardMarkup(request_buttons, resize_keyboard=True)
        request_buttons = build_request_buttons()
        reply_markup = ReplyKeyboardMarkup(request_buttons, resize_keyboard=True)
    else:
        reply_markup = ReplyKeyboardRemove()
    return reply_markup


def uuid_generator():
    return uuid.uuid4().hex


def create_folders():
    os.makedirs("data", exist_ok=True)


def format_datetime(d: datetime):
    """Format datetime for human-readable display (e.g. 15 Feb 2025, 14:30)."""
    if d is None:
        return ""
    return d.strftime("%d %b %Y, %H:%M")


def format_float(f: float):
    """Format number with thousand separators (e.g. 1,000,000) and no trailing zeroes (1.00 -> 1)."""
    if f is None:
        return ""
    s = f"{f:,.2f}".rstrip("0").rstrip(".")
    return s
