from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from common.keyboards import build_admin_keyboard, build_request_buttons
from custom_filters import PrivateChatAndAdmin, PermissionFilter
from models import Permission
from common.lang_dicts import TEXTS, get_lang


async def find_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(Permission.VIEW_IDS).filter(update):
        if update.effective_message.users_shared:
            await update.message.reply_text(
                text=f"<code>{update.effective_message.users_shared.users[0].user_id}</code>",
            )
        else:
            await update.message.reply_text(
                text=f"<code>{update.effective_message.chat_shared.chat_id}</code>",
            )


find_id_handler = MessageHandler(
    filters=filters.StatusUpdate.USERS_SHARED | filters.StatusUpdate.CHAT_SHARED,
    callback=find_id,
)


async def hide_ids_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(Permission.VIEW_IDS).filter(update):
        lang = get_lang(update.effective_user.id)
        if (
            not context.user_data.get("request_keyboard_hidden", None)
            or not context.user_data["request_keyboard_hidden"]
        ):
            context.user_data["request_keyboard_hidden"] = True
            await update.callback_query.delete_message()
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text=TEXTS[lang]["keyboard_hidden"],
                reply_markup=ReplyKeyboardRemove(),
            )
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text=TEXTS[lang]["home_page"],
                reply_markup=build_admin_keyboard(lang, update.effective_user.id),
            )
        else:
            request_buttons = build_request_buttons()
            context.user_data["request_keyboard_hidden"] = False
            await update.callback_query.delete_message()
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text=TEXTS[lang]["keyboard_shown"],
                reply_markup=ReplyKeyboardMarkup(request_buttons, resize_keyboard=True),
            )
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text=TEXTS[lang]["home_page"],
                reply_markup=build_admin_keyboard(lang, update.effective_user.id),
            )


hide_ids_keyboard_handler = CallbackQueryHandler(
    callback=hide_ids_keyboard, pattern="^hide_ids_keyboard$"
)
