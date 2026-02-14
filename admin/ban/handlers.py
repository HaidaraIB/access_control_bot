from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButtonRequestUsers,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from custom_filters import PrivateChatAndAdmin, PermissionFilter
from common.keyboards import (
    build_admin_keyboard,
    build_back_button,
    build_back_to_home_page_button,
)
from common.back_to_home_page import back_to_admin_home_page_handler
from common.lang_dicts import TEXTS, BUTTONS, get_lang
from start import admin_command
import models

USER, CONFIRM = range(2)


async def ban_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(models.Permission.BAN_USERS).filter(update):
        lang = get_lang(update.effective_user.id)
        await update.callback_query.delete_message()
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=TEXTS[lang]["ban_instruction"],
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(
                            text=BUTTONS[lang]["select_user_button"],
                            request_users=KeyboardButtonRequestUsers(
                                request_id=5, user_is_bot=False
                            ),
                        )
                    ]
                ],
                resize_keyboard=True,
            ),
        )
        return USER


async def get_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(models.Permission.BAN_USERS).filter(update):
        lang = get_lang(update.effective_user.id)
        if update.effective_message.users_shared:
            user_id = update.effective_message.users_shared.users[0].user_id
        else:
            user_id = int(update.effective_message.text)

        context.user_data["user_id_to_ban_unban"] = user_id
        with models.session_scope() as s:
            user = s.get(models.User, user_id)
            if not user:
                try:
                    user_chat = await context.bot.get_chat(chat_id=user_id)
                except:
                    await update.message.reply_text(text=TEXTS[lang]["user_not_found"])
                    return
                user = models.User(
                    user_id=user_chat.id,
                    username=user_chat.username if user_chat.username else "",
                    name=user_chat.full_name,
                )
                s.add(user)
                s.commit()

            is_banned = user.is_banned
            user_info = str(user)
            ban_status = (
                TEXTS[lang]["user_banned"]
                if is_banned
                else TEXTS[lang]["user_not_banned"]
            )
            action = (
                TEXTS[lang]["action_unban"] if is_banned else TEXTS[lang]["action_ban"]
            )

        await update.message.reply_text(
            text=TEXTS[lang]["user_found"],
            reply_markup=ReplyKeyboardRemove(),
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    text=BUTTONS[lang]["confirm_button"],
                    callback_data="confirm_ban_unban",
                )
            ],
            build_back_button(data="back_to_get_user_id", lang=lang),
            build_back_to_home_page_button(lang=lang, is_admin=True)[0],
        ]
        await update.message.reply_text(
            text=TEXTS[lang]["ban_confirmation"].format(
                user_info=user_info,
                ban_status=ban_status,
                action=action,
            ),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CONFIRM


async def confirm_ban_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(models.Permission.BAN_USERS).filter(update):
        lang = get_lang(update.effective_user.id)
        user_id = context.user_data["user_id_to_ban_unban"]
        with models.session_scope() as s:
            user = s.get(models.User, user_id)
            user.is_banned = not user.is_banned
            s.commit()

        await update.callback_query.edit_message_text(
            text=TEXTS[lang]["operation_success"],
            reply_markup=build_admin_keyboard(
                lang=lang, user_id=update.effective_user.id
            ),
        )
        return ConversationHandler.END


ban_unban_user_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            ban_unban,
            "^ban_unban$",
        ),
    ],
    states={
        USER: [
            MessageHandler(
                filters=filters.Regex("^\d+$") | filters.StatusUpdate.USERS_SHARED,
                callback=get_user_id,
            ),
        ],
        CONFIRM: [
            CallbackQueryHandler(
                confirm_ban_unban,
                "^confirm_ban_unban$",
            ),
        ],
    },
    fallbacks=[
        admin_command,
        back_to_admin_home_page_handler,
    ],
)
