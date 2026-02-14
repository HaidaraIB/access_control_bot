from telegram import Update, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from common.keyboards import (
    build_admin_keyboard,
    build_back_to_home_page_button,
    build_back_button,
)
from custom_filters import PrivateChatAndAdmin, PermissionFilter
from admin.broadcast.keyboards import build_broadcast_keyboard
from admin.broadcast.functions import send_to
from common.back_to_home_page import back_to_admin_home_page_handler
from common.lang_dicts import TEXTS, get_lang
from start import start_command, admin_command
import models
import asyncio

(
    THE_MESSAGE,
    SEND_TO,
    USERS,
    CHAT_ID,
) = range(4)


async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.BROADCAST
    ).filter(update):
        lang = get_lang(update.effective_user.id)
        await update.callback_query.edit_message_text(
            text=TEXTS[lang]["send_message"],
            reply_markup=InlineKeyboardMarkup(
                build_back_to_home_page_button(lang=lang, is_admin=True)
            ),
        )
        return THE_MESSAGE


async def get_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.BROADCAST
    ).filter(update):
        lang = get_lang(update.effective_user.id)
        if update.message:
            context.user_data["the_message"] = update.message
            await update.message.reply_text(
                text=TEXTS[lang]["send_message_to"],
                reply_markup=build_broadcast_keyboard(lang),
            )
        else:
            await update.callback_query.edit_message_text(
                text=TEXTS[lang]["send_message_to"],
                reply_markup=build_broadcast_keyboard(lang),
            )
        return SEND_TO


back_to_the_message = broadcast_message


async def choose_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.BROADCAST
    ).filter(update):
        lang = get_lang(update.effective_user.id)
        back_buttons = [
            build_back_button("back_to_send_to", lang=lang),
            build_back_to_home_page_button(lang=lang, is_admin=True)[0],
        ]
        if update.callback_query.data == "specific_users":
            await update.callback_query.edit_message_text(
                text=TEXTS[lang]["send_user_ids"],
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
            return USERS
        elif update.callback_query.data == "channel_or_group":
            await update.callback_query.edit_message_text(
                text=TEXTS[lang]["send_chat_id"],
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
            return CHAT_ID

        with models.session_scope() as s:
            if update.callback_query.data == "all_users":
                users = (
                    s.query(models.User)
                    .filter(
                        models.User.is_admin == False, models.User.is_banned == False
                    )
                    .all()
                )
            elif update.callback_query.data == "all_admins":
                users = (
                    s.query(models.User)
                    .filter(
                        models.User.is_admin == True, models.User.is_banned == False
                    )
                    .all()
                )
            elif update.callback_query.data == "everyone":
                users = (
                    s.query(models.User).filter(models.User.is_banned == False).all()
                )

            users = [user.user_id for user in users]

            asyncio.create_task(
                send_to(
                    users=users,
                    context=context,
                )
            )
        await update.callback_query.edit_message_text(
            text=TEXTS[lang]["sending_messages"],
            reply_markup=build_admin_keyboard(lang, update.effective_user.id),
        )

        return ConversationHandler.END


back_to_send_to = get_message


async def get_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.BROADCAST
    ).filter(update):
        lang = get_lang(update.effective_user.id)
        users = set(map(int, update.message.text.split("\n")))
        asyncio.create_task(send_to(users=users, context=context))
        await update.message.reply_text(
            text=TEXTS[lang]["sending_messages"],
            reply_markup=build_admin_keyboard(lang, update.effective_user.id),
        )
        return ConversationHandler.END


async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.BROADCAST
    ).filter(update):
        lang = get_lang(update.effective_user.id)
        chat_id = int(update.message.text)
        try:
            chat = await context.bot.get_chat(chat_id=chat_id)
        except:
            await update.message.reply_text(text=TEXTS[lang]["bot_must_be_member"])
            return
        await send_to(users=[chat_id], context=context)
        await update.message.reply_text(
            text=TEXTS[lang]["message_published_success"].format(chat_title=chat.title),
            reply_markup=build_admin_keyboard(lang, update.effective_user.id),
        )
        return ConversationHandler.END


broadcast_message_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            broadcast_message,
            "^broadcast$",
        )
    ],
    states={
        THE_MESSAGE: [
            MessageHandler(
                filters=(filters.TEXT & ~filters.COMMAND)
                | filters.PHOTO
                | filters.VIDEO
                | filters.AUDIO
                | filters.VOICE
                | filters.CAPTION,
                callback=get_message,
            )
        ],
        SEND_TO: [
            CallbackQueryHandler(
                callback=choose_users,
                pattern=r"^((all)|(specific))_((users)|(admins))$|^everyone$|^channel_or_group$",
            )
        ],
        USERS: [
            MessageHandler(
                filters=filters.Regex(r"^-?[0-9]+(?:\n-?[0-9]+)*$"),
                callback=get_users,
            ),
        ],
        CHAT_ID: [
            MessageHandler(
                filters=filters.Regex(r"^-?[0-9]+(?:\n-?[0-9]+)*$"),
                callback=get_chat_id,
            ),
        ],
    },
    fallbacks=[
        back_to_admin_home_page_handler,
        start_command,
        admin_command,
        CallbackQueryHandler(back_to_the_message, r"^back_to_the_message$"),
        CallbackQueryHandler(back_to_send_to, r"^back_to_send_to$"),
    ],
    name="broadcast_conversation",
    persistent=True,
)
