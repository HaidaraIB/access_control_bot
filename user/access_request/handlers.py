# Access request flow: submit credentials -> admin approve/reject
import logging

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from common.lang_dicts import TEXTS, get_lang
from common.decorators import is_user_banned, add_new_user
from common.keyboards import (
    build_user_keyboard,
    build_back_button,
    build_back_to_home_page_button,
)
from user.access_request.keyboards import build_access_request_keyboard
from custom_filters import PrivateChat
from Config import Config
from start import start_command
from common.back_to_home_page import back_to_user_home_page_handler
import models

logger = logging.getLogger(__name__)

ASK_USERNAME, ASK_PASSWORD = range(2)


@add_new_user
@is_user_banned
async def submit_login_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry: user pressed 'Submit Login Details'. Check no pending, then ask username."""
    if not PrivateChat().filter(update):
        return ConversationHandler.END
    user_id = update.effective_user.id
    with models.session_scope() as s:
        pending_or_approved = (
            s.query(models.AccessRequest)
            .filter(
                models.AccessRequest.user_id == user_id,
                models.AccessRequest.status.in_(
                    (
                        models.AccessRequestStatus.PENDING,
                        models.AccessRequestStatus.APPROVED,
                    )
                ),
            )
            .first()
        )
        if pending_or_approved:
            lang = get_lang(user_id)
            await update.callback_query.answer(
                text=(
                    TEXTS[lang]["access_already_pending"]
                    if pending_or_approved.status == models.AccessRequestStatus.PENDING
                    else TEXTS[lang]["access_already_approved"]
                ),
                show_alert=True,
            )
            return ConversationHandler.END
    lang = get_lang(user_id)
    await update.callback_query.edit_message_text(
        text=TEXTS[lang]["access_ask_username"],
        reply_markup=InlineKeyboardMarkup(
            build_back_to_home_page_button(lang=lang, is_admin=False)
        ),
    )
    return ASK_USERNAME


async def ask_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not PrivateChat().filter(update):
        return ConversationHandler.END
    if update.message:
        context.user_data["access_username"] = (update.message.text or "").strip()
    lang = get_lang(update.effective_user.id)
    back_buttons = [
        build_back_button("back_to_access_ask_password", lang=lang),
        build_back_to_home_page_button(lang=lang, is_admin=False)[0],
    ]
    await update.message.reply_text(
        text=TEXTS[lang]["access_ask_password"],
        reply_markup=InlineKeyboardMarkup(back_buttons),
    )
    return ASK_PASSWORD


back_to_access_ask_password = submit_login_start


async def save_and_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not PrivateChat().filter(update):
        return ConversationHandler.END
    password = (update.message.text or "").strip()
    username = context.user_data.get("access_username") or ""
    user_id = update.effective_user.id
    lang = get_lang(user_id)

    try:
        with models.session_scope() as s:
            req = models.AccessRequest(
                user_id=user_id,
                submitted_username=username,
                submitted_password=password,
                status=models.AccessRequestStatus.PENDING,
            )
            s.add(req)
            s.flush()
            req_id = req.id
    except Exception as e:
        logger.exception("Access request save failed: %s", e)
        await update.message.reply_text(
            text=TEXTS[lang]["access_request_save_failed"],
        )
        return ConversationHandler.END

    try:
        owner_lang = models.Language.ARABIC
        with models.session_scope() as s:
            owner = s.get(models.User, Config.OWNER_ID)
            user = s.get(models.User, update.effective_user.id)
            owner_lang = owner.lang
        keyboard = build_access_request_keyboard(req_id, owner_lang)
        await context.bot.send_message(
            chat_id=Config.OWNER_ID,
            text=TEXTS[owner_lang]["access_request_message"].format(
                title=TEXTS[owner_lang]["access_request_message_title"],
                user=f"@{user.username}" if user.username else user.name,
                username=username,
                password=password,
                req_id=req_id,
            ),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    except Exception as e:
        logger.exception("Failed to forward access request to admin: %s", e)

    logger.info("New access request request_id=%s user_id=%s", req_id, user_id)
    await update.message.reply_text(
        text=TEXTS[lang]["access_request_received"],
        reply_markup=build_user_keyboard(lang),
    )
    context.user_data.pop("access_username", None)
    return ConversationHandler.END


access_request_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            submit_login_start,
            r"^submit_login_details$",
        ),
    ],
    states={
        ASK_USERNAME: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                callback=ask_password,
            ),
        ],
        ASK_PASSWORD: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND,
                callback=save_and_forward,
            ),
        ],
    },
    fallbacks=[
        start_command,
        back_to_user_home_page_handler,
        CallbackQueryHandler(
            back_to_access_ask_password, r"^back_to_access_ask_password$"
        ),
    ],
    name="access_request_conversation",
    persistent=True,
)
