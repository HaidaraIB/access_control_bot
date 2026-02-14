from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButtonRequestChat,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from admin.force_join_chats_settings.keyboards import build_force_join_chats_keyboard
from common.back_to_home_page import back_to_admin_home_page_handler
from common.keyboards import (
    build_admin_keyboard,
    build_back_to_home_page_button,
    build_back_button,
)
from common.lang_dicts import TEXTS, BUTTONS, get_lang
from custom_filters import PrivateChatAndAdmin, PermissionFilter
from start import admin_command
import models


async def force_join_chats_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.MANAGE_FORCE_JOIN
    ).filter(update):
        lang = get_lang(update.effective_user.id)
        keyboard = build_force_join_chats_keyboard(lang)
        keyboard.append(build_back_to_home_page_button(lang=lang, is_admin=True)[0])
        await update.callback_query.edit_message_text(
            text=TEXTS[lang]["force_join_chats_title"],
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return ConversationHandler.END


force_join_chats_settings_handler = CallbackQueryHandler(
    force_join_chats_settings,
    "^force_join_chats_settings$|^back_to_force_join_chats_settings$",
)

CHAT_ID, CHAT_LINK = range(2)


async def add_force_join_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.MANAGE_FORCE_JOIN
    ).filter(update):
        lang = get_lang(update.effective_user.id)
        await update.callback_query.answer()
        await update.callback_query.delete_message()
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=TEXTS[lang]["add_force_join_chat_instruction"],
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(
                            text=BUTTONS[lang]["channel"],
                            request_chat=KeyboardButtonRequestChat(
                                request_id=6,
                                chat_is_channel=True,
                            ),
                        ),
                        KeyboardButton(
                            text=BUTTONS[lang]["group"],
                            request_chat=KeyboardButtonRequestChat(
                                request_id=7,
                                chat_is_channel=False,
                            ),
                        ),
                    ]
                ],
                resize_keyboard=True,
            ),
        )
        return CHAT_ID


async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.MANAGE_FORCE_JOIN
    ).filter(update):
        lang = get_lang(update.effective_user.id)

        if update.effective_message.chat_shared:
            chat_id = update.effective_message.chat_shared.chat_id
        else:
            try:
                chat_id = int(update.message.text)
            except ValueError:
                await update.message.reply_text(
                    text=TEXTS[lang]["invalid_chat_id"],
                    reply_markup=ReplyKeyboardRemove(),
                )
                await update.message.reply_text(
                    text=TEXTS[lang]["home_page"],
                    reply_markup=build_admin_keyboard(lang, update.effective_user.id),
                )
                return ConversationHandler.END

        # Get chat info
        try:
            chat = await context.bot.get_chat(chat_id=chat_id)

            # Try to get invite link, if not available, use username or ask for link
            chat_link = None
            if hasattr(chat, "invite_link") and chat.invite_link:
                chat_link = chat.invite_link
            elif hasattr(chat, "username") and chat.username:
                chat_link = f"https://t.me/{chat.username}"

            context.user_data["force_join_chat_id"] = chat_id
            context.user_data["force_join_chat_title"] = (
                chat.title if hasattr(chat, "title") else f"Chat {chat_id}"
            )

            # If we have a link, use it directly, otherwise ask for it
            if chat_link:
                context.user_data["force_join_chat_link"] = chat_link
                # Add directly without asking for link
                with models.session_scope() as s:
                    # Check if chat already exists
                    existing = (
                        s.query(models.ForceJoinChat)
                        .filter(models.ForceJoinChat.chat_id == chat_id)
                        .first()
                    )

                    if existing:
                        existing.chat_link = chat_link
                        existing.chat_title = context.user_data["force_join_chat_title"]
                    else:
                        new_chat = models.ForceJoinChat(
                            chat_id=chat_id,
                            chat_link=chat_link,
                            chat_title=context.user_data["force_join_chat_title"],
                        )
                        s.add(new_chat)

                # Clean up user_data
                context.user_data.pop("force_join_chat_id", None)
                context.user_data.pop("force_join_chat_link", None)
                context.user_data.pop("force_join_chat_title", None)

                await update.message.reply_text(
                    text=TEXTS[lang]["force_join_chat_added_success"],
                    reply_markup=ReplyKeyboardRemove(),
                )
                await update.message.reply_text(
                    text=TEXTS[lang]["home_page"],
                    reply_markup=build_admin_keyboard(lang, update.effective_user.id),
                )
                return ConversationHandler.END
            else:
                # No link available, ask user to provide it
                await update.message.reply_text(
                    text=TEXTS[lang]["enter_chat_link_instruction"].format(
                        chat_title=context.user_data["force_join_chat_title"]
                    ),
                    reply_markup=ReplyKeyboardRemove(),
                )
                return CHAT_LINK
        except Exception as e:
            await update.message.reply_text(
                text=TEXTS[lang]["chat_not_found"],
                reply_markup=ReplyKeyboardRemove(),
            )
            await update.message.reply_text(
                text=TEXTS[lang]["home_page"],
                reply_markup=build_admin_keyboard(lang, update.effective_user.id),
            )
            return ConversationHandler.END


async def get_chat_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.MANAGE_FORCE_JOIN
    ).filter(update):
        lang = get_lang(update.effective_user.id)
        chat_link = update.message.text.strip()

        # Normalize link format - convert @username to https://t.me/username
        if chat_link.startswith("@"):
            chat_link = f"https://t.me/{chat_link[1:]}"
        elif not chat_link.startswith("https://t.me/") and not chat_link.startswith(
            "http://t.me/"
        ):
            await update.message.reply_text(
                text=TEXTS[lang]["invalid_chat_link"],
            )
            return CHAT_LINK

        chat_id = context.user_data.get("force_join_chat_id")
        chat_title = context.user_data.get("force_join_chat_title", "")

        with models.session_scope() as s:
            # Check if chat already exists
            existing = (
                s.query(models.ForceJoinChat)
                .filter(models.ForceJoinChat.chat_id == chat_id)
                .first()
            )

            if existing:
                existing.chat_link = chat_link
                existing.chat_title = chat_title
            else:
                # Get max order to add at the end
                max_order_result = (
                    s.query(models.ForceJoinChat.order)
                    .order_by(models.ForceJoinChat.order.desc())
                    .first()
                )
                new_order = (max_order_result[0] + 1) if max_order_result else 0

                new_chat = models.ForceJoinChat(
                    chat_id=chat_id,
                    chat_link=chat_link,
                    chat_title=chat_title,
                    order=new_order,
                )
                s.add(new_chat)

        # Clean up user_data
        context.user_data.pop("force_join_chat_id", None)
        context.user_data.pop("force_join_chat_link", None)
        context.user_data.pop("force_join_chat_title", None)

        await update.message.reply_text(
            text=TEXTS[lang]["force_join_chat_added_success"],
            reply_markup=ReplyKeyboardRemove(),
        )
        await update.message.reply_text(
            text=TEXTS[lang]["home_page"],
            reply_markup=build_admin_keyboard(lang, update.effective_user.id),
        )
        return ConversationHandler.END


add_force_join_chat_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=add_force_join_chat,
            pattern="^add_force_join_chat$",
        ),
    ],
    states={
        CHAT_ID: [
            MessageHandler(
                filters=filters.Regex(r"^-?\d+$"),
                callback=get_chat_id,
            ),
            MessageHandler(
                filters=filters.StatusUpdate.CHAT_SHARED,
                callback=get_chat_id,
            ),
        ],
        CHAT_LINK: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND,
                callback=get_chat_link,
            ),
        ],
    },
    fallbacks=[
        force_join_chats_settings_handler,
        admin_command,
        back_to_admin_home_page_handler,
    ],
)


CHOOSE_CHAT_TO_REMOVE = range(1)


async def remove_force_join_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.MANAGE_FORCE_JOIN
    ).filter(update):
        lang = get_lang(update.effective_user.id)
        with models.session_scope() as s:
            if update.callback_query.data.isnumeric():
                chat = s.get(models.ForceJoinChat, int(update.callback_query.data))
                s.delete(chat)
                s.commit()
                await update.callback_query.answer(
                    text=TEXTS[lang]["force_join_chat_removed_success"],
                    show_alert=True,
                )

            chats = s.query(models.ForceJoinChat).all()

            if not chats:
                await update.callback_query.answer(
                    text=TEXTS[lang]["no_force_join_chats"],
                    show_alert=True,
                )
                if update.callback_query.data.isnumeric():
                    await update.callback_query.edit_message_text(
                        text=TEXTS[lang]["home_page"],
                        reply_markup=build_admin_keyboard(
                            lang=lang, user_id=update.effective_user.id
                        ),
                    )
                return ConversationHandler.END

            chat_keyboard = [
                [
                    InlineKeyboardButton(
                        text=chat.chat_title or f"Chat {chat.chat_id}",
                        callback_data=str(chat.id),
                    ),
                ]
                for chat in chats
            ]
        chat_keyboard.append(
            build_back_button("back_to_force_join_chats_settings", lang=lang)
        )
        chat_keyboard.append(
            build_back_to_home_page_button(lang=lang, is_admin=True)[0]
        )
        await update.callback_query.edit_message_text(
            text=TEXTS[lang]["remove_force_join_chat_instruction"],
            reply_markup=InlineKeyboardMarkup(chat_keyboard),
        )
        return CHOOSE_CHAT_TO_REMOVE


remove_force_join_chat_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=remove_force_join_chat,
            pattern="^remove_force_join_chat$",
        ),
    ],
    states={
        CHOOSE_CHAT_TO_REMOVE: [
            CallbackQueryHandler(
                remove_force_join_chat,
                "^\d+$",
            ),
        ]
    },
    fallbacks=[
        force_join_chats_settings_handler,
        admin_command,
        back_to_admin_home_page_handler,
    ],
)


async def show_force_join_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.MANAGE_FORCE_JOIN
    ).filter(update):
        lang = get_lang(update.effective_user.id)
        with models.session_scope() as s:
            chats = s.query(models.ForceJoinChat).all()

            if not chats:
                await update.callback_query.answer(
                    text=TEXTS[lang]["no_force_join_chats"],
                    show_alert=True,
                )
                return
            text = TEXTS[lang]["force_join_chats_list_title"] + "\n\n"
            for chat in chats:
                text += str(chat) + "\n\n"
            text += TEXTS[lang]["continue_with_admin_command"]

        keyboard = [
            build_back_button("back_to_force_join_chats_settings", lang=lang),
            build_back_to_home_page_button(lang=lang, is_admin=True)[0],
        ]
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


show_force_join_chats_handler = CallbackQueryHandler(
    callback=show_force_join_chats,
    pattern="^show_force_join_chats$",
)
