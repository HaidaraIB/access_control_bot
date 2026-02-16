# Admin: handle access requests (approve/reject, settings, history)
import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ChatMemberStatus
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    ChatMemberHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)

from common.lang_dicts import TEXTS, BUTTONS, get_lang
from common.common import format_datetime
from common.keyboards import build_back_button, build_back_to_home_page_button
from common.back_to_home_page import back_to_admin_home_page_handler
from admin.access_requests.keyboards import (
    build_access_request_keyboard,
    build_access_requests_settings_keyboard,
    build_access_request_history_keyboard,
)
from custom_filters import PrivateChatAndAdmin, PermissionFilter
from Config import Config
from start import admin_command
import models

logger = logging.getLogger(__name__)

WAIT_ACCESS_REQUEST_ID = 0

_STATUS_TEXT_KEYS = {
    models.AccessRequestStatus.PENDING: "status_pending",
    models.AccessRequestStatus.APPROVED: "status_approved",
    models.AccessRequestStatus.REJECTED: "status_rejected",
}


def _access_request_details_text(
    req: models.AccessRequest, lang: models.Language, user_display: str
):
    status_text = TEXTS[lang].get(
        _STATUS_TEXT_KEYS.get(req.status, "status_pending"), str(req.status)
    )
    created = format_datetime(req.created_at)
    if req.order_id:
        return TEXTS[lang]["access_request_details_text_order_id"].format(
            id=req.id,
            user=user_display,
            order_id=req.order_id,
            status=status_text,
            created_at=created,
        )
    return TEXTS[lang]["access_request_details_text"].format(
        id=req.id,
        user=user_display,
        username=req.submitted_username or "—",
        password=req.submitted_password or "—",
        status=status_text,
        created_at=created,
    )


async def access_requests_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show access requests settings: 4 buttons (request pending, history, back, back to home)."""
    if not PrivateChatAndAdmin().filter(update) or not PermissionFilter(
        models.Permission.MANAGE_ACCESS_REQUESTS
    ).filter(update):
        return ConversationHandler.END
    lang = get_lang(update.effective_user.id)
    keyboard = build_access_requests_settings_keyboard(lang)
    keyboard.append(build_back_to_home_page_button(lang=lang, is_admin=True)[0])
    await update.callback_query.edit_message_text(
        text=TEXTS[lang]["access_requests_settings_title"],
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return ConversationHandler.END


async def access_request_history_show(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Show access request history: ask for id with keyboard of last 20 access requests + back + back to home."""
    if not PrivateChatAndAdmin().filter(update) or not PermissionFilter(
        models.Permission.MANAGE_ACCESS_REQUESTS
    ).filter(update):
        return ConversationHandler.END
    lang = get_lang(update.effective_user.id)
    with models.session_scope() as s:
        access_requests = (
            s.query(models.AccessRequest)
            .order_by(models.AccessRequest.created_at.desc())
            .limit(20)
            .all()
        )
    keyboard = build_access_request_history_keyboard(access_requests, lang)
    keyboard.append(build_back_button("back_to_access_request_history_show", lang=lang))
    keyboard.append(build_back_to_home_page_button(lang=lang, is_admin=True)[0])
    await update.callback_query.edit_message_text(
        text=TEXTS[lang]["access_request_history_ask_id"],
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return WAIT_ACCESS_REQUEST_ID


back_to_access_request_history_show = access_requests_settings


async def show_access_request_details(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Handle pressing an access request button or sending id: show access request details."""
    if not PrivateChatAndAdmin().filter(update) or not PermissionFilter(
        models.Permission.MANAGE_ACCESS_REQUESTS
    ).filter(update):
        return ConversationHandler.END
    lang = get_lang(update.effective_user.id)

    if update.message:
        req_id = int(update.message.text.strip())
    else:
        req_id = int(update.callback_query.data.replace("access_request_id_", ""))

    user_display = None
    with models.session_scope() as s:
        req = s.get(models.AccessRequest, req_id)
        user_display = f"@{req.user.username}" if req.user.username else req.user.name

    if not req:
        if update.callback_query:
            await update.callback_query.answer(
                text=TEXTS[lang]["access_not_found"],
                show_alert=True,
            )
        else:
            await update.message.reply_text(
                text=TEXTS[lang]["access_not_found"],
            )
        return WAIT_ACCESS_REQUEST_ID

    text = _access_request_details_text(req, lang, user_display)
    back_buttons = [
        build_back_button("back_to_show_access_request_details", lang=lang),
        build_back_to_home_page_button(lang=lang, is_admin=True)[0],
    ]
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return WAIT_ACCESS_REQUEST_ID
    await update.message.reply_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(back_buttons),
    )
    return WAIT_ACCESS_REQUEST_ID


back_to_show_access_request_details = access_request_history_show

access_requests_settings_handler = CallbackQueryHandler(
    access_requests_settings,
    "^access_requests_settings$",
)


access_request_history_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            access_request_history_show,
            r"^access_request_history$",
        ),
    ],
    states={
        WAIT_ACCESS_REQUEST_ID: [
            MessageHandler(
                filters=filters.Regex(r"^[0-9]+$"),
                callback=show_access_request_details,
            ),
            CallbackQueryHandler(
                show_access_request_details,
                pattern=r"^access_request_id_\d+$",
            ),
        ],
    },
    fallbacks=[
        admin_command,
        back_to_admin_home_page_handler,
        CallbackQueryHandler(
            back_to_access_request_history_show, "^back_to_access_request_history_show$"
        ),
        CallbackQueryHandler(
            back_to_show_access_request_details, "^back_to_show_access_request_details$"
        ),
    ],
    name="access_request_history_conversation",
    persistent=True,
)


async def request_pending_access_request(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Send the oldest pending access request to the admin with approve/reject buttons, then delete the menu message."""
    if not PrivateChatAndAdmin().filter(update) or not PermissionFilter(
        models.Permission.MANAGE_ACCESS_REQUESTS
    ).filter(update):
        return
    lang = get_lang(update.effective_user.id)
    with models.session_scope() as s:
        oldest = (
            s.query(models.AccessRequest)
            .filter(models.AccessRequest.status == models.AccessRequestStatus.PENDING)
            .order_by(models.AccessRequest.created_at.asc())
            .first()
        )
        if oldest:
            u = oldest.user
            user_display = (
                f"@{u.username}"
                if u and u.username
                else (u.name if u else str(oldest.user_id))
            )
    if not oldest:
        await update.callback_query.answer(
            text=TEXTS[lang]["no_pending_access_requests"],
            show_alert=True,
        )
        return
    req_id = oldest.id
    if oldest.order_id:
        text = TEXTS[lang]["access_request_message_order_id"].format(
            title=TEXTS[lang]["access_request_message_title"],
            user=user_display,
            order_id=oldest.order_id,
            req_id=req_id,
        )
    else:
        text = TEXTS[lang]["access_request_message"].format(
            title=TEXTS[lang]["access_request_message_title"],
            user=user_display,
            username=oldest.submitted_username or "—",
            password=oldest.submitted_password or "—",
            req_id=req_id,
        )
    keyboard = build_access_request_keyboard(req_id, lang)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    await update.callback_query.delete_message()


request_pending_access_request_handler = CallbackQueryHandler(
    request_pending_access_request,
    "^request_pending_access_request$",
)


async def access_approve_reject_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Handle Approve/Reject buttons on access request messages."""
    if not PrivateChatAndAdmin().filter(update) or not PermissionFilter(
        models.Permission.MANAGE_ACCESS_REQUESTS
    ).filter(update):
        return
    owner_lang = get_lang(update.effective_user.id)
    data = update.callback_query.data
    try:
        req_id = int(data.split("_")[-1])
    except (ValueError, IndexError):
        await update.callback_query.answer(text="Invalid request.", show_alert=True)
        return
    approved = data.startswith("access_approve_")
    with models.session_scope() as s:
        req = s.get(models.AccessRequest, req_id)
        if not req:
            await update.callback_query.answer(
                text=TEXTS[owner_lang]["access_not_found"],
                show_alert=True,
            )
            return
        if req.status != models.AccessRequestStatus.PENDING:
            await update.callback_query.answer(
                text=TEXTS[owner_lang]["access_request_already_processed"],
                show_alert=True,
            )
            return
        req.status = (
            models.AccessRequestStatus.APPROVED
            if approved
            else models.AccessRequestStatus.REJECTED
        )
        user_id = req.user_id
        try:
            usr = s.get(models.User, user_id)
            user_lang = usr.lang if usr else models.Language.ARABIC
        except Exception:
            user_lang = models.Language.ARABIC

    try:
        if approved:
            btn_text = BUTTONS[owner_lang]["access_request_approved"]
        else:
            btn_text = BUTTONS[owner_lang]["access_request_rejected"]
        await update.callback_query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup.from_button(
                InlineKeyboardButton(text=btn_text, callback_data=btn_text)
            )
        )
    except Exception:
        pass
    try:
        if approved:
            invite_link_obj = await context.bot.create_chat_invite_link(
                chat_id=Config.PRIVATE_CHANNEL_ID,
                member_limit=1,
            )
            await context.bot.send_message(
                chat_id=user_id,
                text=TEXTS[user_lang]["access_approved_with_link_msg"].format(
                    invite_link=invite_link_obj.invite_link
                ),
            )
            with models.session_scope() as s:
                r = s.get(models.AccessRequest, req_id)
                if r:
                    r.invite_link = invite_link_obj.invite_link
        else:
            await context.bot.send_message(
                chat_id=user_id,
                text=TEXTS[user_lang]["access_rejected_msg"],
            )
    except Exception as e:
        logger.warning("Failed to notify user %s: %s", user_id, e)

    logger.info(
        "Access request %s: request_id=%s user_id=%s by admin_id=%s",
        "approved" if approved else "rejected",
        req_id,
        user_id,
        update.effective_user.id,
    )


access_approve_reject_handler = CallbackQueryHandler(
    access_approve_reject_callback,
    pattern=r"^access_(approve|reject)_\d+$",
)


async def access_invite_link_join_revoke(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """When a user joins the private channel via an access-request invite link, revoke that link."""
    channel_id = Config.PRIVATE_CHANNEL_ID
    if not channel_id:
        return
    cm = update.chat_member
    if not cm or cm.chat.id != channel_id:
        return
    old_status = cm.old_chat_member.status if cm.old_chat_member else None
    new_status = cm.new_chat_member.status if cm.new_chat_member else None
    member_statuses = (
        ChatMemberStatus.OWNER,
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.RESTRICTED,
    )
    left_statuses = (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED)
    if new_status not in member_statuses or old_status not in left_statuses:
        return
    user_id = cm.new_chat_member.user.id if cm.new_chat_member else None
    if not user_id:
        return
    req_id = None
    with models.session_scope() as s:
        req = (
            s.query(models.AccessRequest)
            .filter(models.AccessRequest.invite_link == cm.invite_link.invite_link)
            .first()
        )
        if not req:
            return
        req.is_revoked = True
        invite_link = req.invite_link
        req_id = req.id
    try:
        await context.bot.revoke_chat_invite_link(
            chat_id=channel_id,
            invite_link=invite_link,
        )
        logger.info(
            "Revoked access invite link after user joined: user_id=%s request_id=%s",
            user_id,
            req_id,
        )
    except Exception as e:
        logger.warning(
            "Failed to revoke access invite link (user_id=%s): %s", user_id, e
        )


access_invite_link_join_revoke_handler = ChatMemberHandler(
    access_invite_link_join_revoke,
    chat_member_types=ChatMemberHandler.CHAT_MEMBER,
    chat_id=Config.PRIVATE_CHANNEL_ID,
)
