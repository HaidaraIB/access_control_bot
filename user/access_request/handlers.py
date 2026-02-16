# Access request flow: submit credentials -> admin approve/reject
import logging

from telegram import Update, InlineKeyboardMarkup
from telegram.constants import ChatMemberStatus
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
from user.access_request.keyboards import (
    build_access_request_keyboard,
    build_submit_method_keyboard,
)
from custom_filters import PrivateChat
from Config import Config
from start import start_command
from common.back_to_home_page import back_to_user_home_page_handler
import models

logger = logging.getLogger(__name__)

CHOOSE_METHOD, ASK_USERNAME, ASK_PASSWORD, ASK_ORDER_ID = range(4)


async def _is_user_already_member(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    lang: models.Language = models.Language.ARABIC,
):
    try:
        chat_member = await context.bot.get_chat_member(
            chat_id=Config.PRIVATE_CHANNEL_ID,
            user_id=update.effective_user.id,
        )
        if chat_member.status not in (
            ChatMemberStatus.LEFT,
            ChatMemberStatus.BANNED,
        ):
            await update.callback_query.answer(
                text=TEXTS[lang]["access_already_in_channel"],
                show_alert=True,
            )
            return True
    except Exception as e:
        logger.exception("Error checking if user is already member: %s", e)
    return False


async def _is_user_has_pending_request(
    update: Update, lang: models.Language = models.Language.ARABIC
):
    with models.session_scope() as s:
        pending = (
            s.query(models.AccessRequest)
            .filter(
                models.AccessRequest.user_id == update.effective_user.id,
                models.AccessRequest.status == models.AccessRequestStatus.PENDING,
            )
            .first()
        )
        if pending:
            await update.callback_query.answer(
                text=TEXTS[lang]["access_already_pending"],
                show_alert=True,
            )
            return True
    return False


def _get_unrevoked_invite_link(user_id: int) -> str | None:
    """Return invite_link if user has an approved request with unrevoked link, else None."""
    with models.session_scope() as s:
        req = (
            s.query(models.AccessRequest)
            .filter(
                models.AccessRequest.user_id == user_id,
                models.AccessRequest.status == models.AccessRequestStatus.APPROVED,
                models.AccessRequest.invite_link.isnot(None),
                models.AccessRequest.is_revoked == False,  # noqa: E712
            )
            .first()
        )
        return req.invite_link if req else None


@add_new_user
@is_user_banned
async def submit_login_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not PrivateChat().filter(update):
        return ConversationHandler.END

    lang = get_lang(update.effective_user.id)

    user_alredy_member = await _is_user_already_member(
        update=update, context=context, lang=lang
    )
    if user_alredy_member:
        return ConversationHandler.END

    user_has_pending_request = await _is_user_has_pending_request(
        update=update, lang=lang
    )
    if user_has_pending_request:
        return ConversationHandler.END

    # If user has an approved request with unrevoked invite link, send it and end
    invite_link = _get_unrevoked_invite_link(update.effective_user.id)
    if invite_link:
        await update.callback_query.edit_message_text(
            text=TEXTS[lang]["access_approved_with_link_msg"].format(
                invite_link=invite_link
            ),
        )
        return ConversationHandler.END

    keyboard = build_submit_method_keyboard(lang)
    keyboard.extend(build_back_to_home_page_button(lang=lang, is_admin=False))
    await update.callback_query.edit_message_text(
        text=TEXTS[lang]["access_choose_method"],
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return CHOOSE_METHOD


async def choose_username_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not PrivateChat().filter(update):
        return ConversationHandler.END
    lang = get_lang(update.effective_user.id)
    back_buttons = [
        build_back_button("back_to_access_choose_method", lang=lang),
        build_back_to_home_page_button(lang=lang, is_admin=False)[0],
    ]
    await update.callback_query.edit_message_text(
        text=TEXTS[lang]["access_ask_username"],
        reply_markup=InlineKeyboardMarkup(back_buttons),
    )
    return ASK_USERNAME


async def choose_order_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not PrivateChat().filter(update):
        return ConversationHandler.END
    lang = get_lang(update.effective_user.id)
    back_buttons = [
        build_back_button("back_to_access_choose_method", lang=lang),
        build_back_to_home_page_button(lang=lang, is_admin=False)[0],
    ]
    await update.callback_query.edit_message_text(
        text=TEXTS[lang]["access_ask_order_id"],
        reply_markup=InlineKeyboardMarkup(back_buttons),
    )
    return ASK_ORDER_ID


back_to_access_choose_method = submit_login_start


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


back_to_access_ask_password = choose_username_password


async def _save_access_request(
    update: Update,
    user_id: int,
    username: str = None,
    password: str = None,
    order_id: str = None,
    lang: models.Language = models.Language.ARABIC,
):
    req_id = None
    try:
        with models.session_scope() as s:
            req = models.AccessRequest(
                user_id=user_id,
                submitted_username=username,
                submitted_password=password,
                order_id=order_id,
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
    return req_id


async def _forward_access_request_to_owner(
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int,
    req_id: int,
    username: str = None,
    password: str = None,
    order_id: int = None,
):
    try:
        owner_lang = models.Language.ARABIC
        with models.session_scope() as s:
            owner = s.get(models.User, Config.OWNER_ID)
            user = s.get(models.User, user_id)
            owner_lang = owner.lang
        keyboard = build_access_request_keyboard(req_id, owner_lang)
        if order_id:
            request_details = TEXTS[owner_lang][
                "access_request_message_order_id"
            ].format(
                title=TEXTS[owner_lang]["access_request_message_title"],
                user=f"@{user.username}" if user.username else user.name,
                order_id=order_id,
                req_id=req_id,
            )
        else:
            request_details = TEXTS[owner_lang]["access_request_message"].format(
                title=TEXTS[owner_lang]["access_request_message_title"],
                user=f"@{user.username}" if user.username else user.name,
                username=username,
                password=password,
                req_id=req_id,
            )
        await context.bot.send_message(
            chat_id=Config.OWNER_ID,
            text=request_details,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    except Exception as e:
        logger.exception("Failed to forward access request to admin: %s", e)


async def save_and_forward_username_password(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    if not PrivateChat().filter(update):
        return ConversationHandler.END

    user_id = update.effective_user.id
    lang = get_lang(user_id)

    password = (update.message.text or "").strip()
    username = context.user_data.get("access_username") or ""

    req_id = await _save_access_request(
        update=update,
        user_id=user_id,
        username=username,
        password=password,
        lang=lang,
    )
    if not req_id:
        return ConversationHandler.END

    await _forward_access_request_to_owner(
        context=context,
        user_id=user_id,
        req_id=req_id,
        username=username,
        password=password,
    )

    await update.message.reply_text(
        text=TEXTS[lang]["access_request_received"],
        reply_markup=build_user_keyboard(lang),
    )
    context.user_data.pop("access_username", None)
    return ConversationHandler.END


async def save_and_forward_order_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not PrivateChat().filter(update):
        return ConversationHandler.END

    user_id = update.effective_user.id
    lang = get_lang(user_id)

    order_id = (update.message.text or "").strip()

    req_id = await _save_access_request(
        update=update,
        user_id=user_id,
        order_id=order_id,
        lang=lang,
    )
    if not req_id:
        return ConversationHandler.END

    await _forward_access_request_to_owner(
        context=context,
        user_id=user_id,
        req_id=req_id,
        order_id=order_id,
    )
    logger.info(
        "New access request (order_id) request_id=%s user_id=%s", req_id, user_id
    )
    await update.message.reply_text(
        text=TEXTS[lang]["access_request_received"],
        reply_markup=build_user_keyboard(lang),
    )
    return ConversationHandler.END


access_request_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            submit_login_start,
            r"^submit_login_details$",
        ),
    ],
    states={
        CHOOSE_METHOD: [
            CallbackQueryHandler(
                choose_username_password,
                r"^submit_login_username_password$",
            ),
            CallbackQueryHandler(
                choose_order_id,
                r"^submit_login_order_id$",
            ),
        ],
        ASK_USERNAME: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                callback=ask_password,
            ),
        ],
        ASK_PASSWORD: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND,
                callback=save_and_forward_username_password,
            ),
        ],
        ASK_ORDER_ID: [
            MessageHandler(
                filters=filters.Regex(r"^[0-9]+$"),
                callback=save_and_forward_order_id,
            ),
        ],
    },
    fallbacks=[
        start_command,
        back_to_user_home_page_handler,
        CallbackQueryHandler(
            back_to_access_choose_method, r"^back_to_access_choose_method$"
        ),
        CallbackQueryHandler(
            back_to_access_ask_password, r"^back_to_access_ask_password$"
        ),
    ],
    name="access_request_conversation",
    persistent=True,
)
