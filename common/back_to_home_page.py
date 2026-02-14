from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler
from common.decorators import is_user_member, is_user_banned
from common.keyboards import build_user_keyboard, build_admin_keyboard
from common.lang_dicts import TEXTS, get_lang
from custom_filters import PrivateChat, PrivateChatAndAdmin


@is_user_banned
@is_user_member
async def back_to_user_home_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChat().filter(update):
        lang = get_lang(update.effective_user.id)
        await update.callback_query.edit_message_text(
            text=TEXTS[lang]["home_page"],
            reply_markup=build_user_keyboard(lang),
        )
        return ConversationHandler.END


async def back_to_admin_home_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update):
        lang = get_lang(update.effective_user.id)
        await update.callback_query.edit_message_text(
            text=TEXTS[lang]["home_page"],
            reply_markup=build_admin_keyboard(lang, update.effective_user.id),
        )
        return ConversationHandler.END


back_to_user_home_page_handler = CallbackQueryHandler(
    back_to_user_home_page, "^back_to_user_home_page$"
)
back_to_admin_home_page_handler = CallbackQueryHandler(
    back_to_admin_home_page, "^back_to_admin_home_page$"
)
