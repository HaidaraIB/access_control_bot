from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.constants import ChatMemberStatus
from common.keyboards import build_user_keyboard
from common.lang_dicts import TEXTS, BUTTONS, get_lang
from common.decorators import is_user_banned
import models


async def check_if_user_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get all force join chats from database
    with models.session_scope() as s:
        force_join_chats = s.query(models.ForceJoinChat).all()

    # If no force join chats are configured, allow access
    if not force_join_chats:
        return True

    # Check membership for all chats
    chats_not_joined: list[models.ForceJoinChat] = []
    for chat in force_join_chats:
        try:
            chat_member = await context.bot.get_chat_member(
                chat_id=chat.chat_id,
                user_id=update.effective_user.id,
            )
            if chat_member.status == ChatMemberStatus.LEFT:
                chats_not_joined.append(chat)
        except Exception:
            # If we can't check membership (e.g., bot not admin), skip this chat
            continue

    # If user has joined all chats, allow access
    if not chats_not_joined:
        return True

    # User hasn't joined all required chats
    lang = get_lang(update.effective_user.id)

    # Build buttons for all chats that need to be joined
    buttons = []
    for chat in chats_not_joined:
        buttons.append(
            InlineKeyboardButton(
                text=chat.chat_title if chat.chat_title else f"Chat: {chat.id}",
                url=chat.chat_link,
            )
        )

    # Add verify button
    buttons.append(
        InlineKeyboardButton(
            text=BUTTONS[lang]["check_joined"],
            callback_data="check_joined",
        )
    )

    markup = InlineKeyboardMarkup.from_column(buttons)

    # Update message text based on number of chats
    if len(chats_not_joined) == 1:
        force_join_text = TEXTS[lang]["force_join_msg"]
    else:
        force_join_text = TEXTS[lang]["force_join_multiple_msg"]

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=force_join_text,
            reply_markup=markup,
        )
    else:
        await update.message.reply_text(
            text=force_join_text,
            reply_markup=markup,
        )
    return False


@is_user_banned
async def check_joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get all force join chats from database
    with models.session_scope() as s:
        force_join_chats = s.query(models.ForceJoinChat).all()

    # If no force join chats are configured, allow access
    if not force_join_chats:
        lang = get_lang(update.effective_user.id)
        await update.callback_query.edit_message_text(
            text=TEXTS[lang]["welcome_msg"],
            reply_markup=build_user_keyboard(lang),
        )
        return

    # Check membership for all chats
    chats_not_joined = []
    for chat in force_join_chats:
        try:
            chat_member = await context.bot.get_chat_member(
                chat_id=chat.chat_id,
                user_id=update.effective_user.id,
            )
            if chat_member.status == ChatMemberStatus.LEFT:
                chats_not_joined.append(chat)
        except Exception:
            # If we can't check membership, assume user hasn't joined
            chats_not_joined.append(chat)

    lang = get_lang(update.effective_user.id)

    # If user hasn't joined all chats, show error
    if chats_not_joined:
        if len(chats_not_joined) == 1:
            error_text = TEXTS[lang]["join_first_answer"]
        else:
            error_text = TEXTS[lang]["join_all_first_answer"]
        await update.callback_query.answer(
            text=error_text,
            show_alert=True,
        )
        return

    # User has joined all chats
    await update.callback_query.edit_message_text(
        text=TEXTS[lang]["welcome_msg"],
        reply_markup=build_user_keyboard(lang),
    )


check_joined_handler = CallbackQueryHandler(
    callback=check_joined,
    pattern="^check_joined$",
)
