from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButtonRequestUsers,
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
import sqlalchemy as sa
from admin.admin_settings.keyboards import (
    build_admin_settings_keyboard,
    build_permissions_keyboard,
)
from common.back_to_home_page import back_to_admin_home_page_handler
from common.keyboards import (
    build_admin_keyboard,
    build_back_to_home_page_button,
    build_back_button,
    build_keyboard,
)
from common.lang_dicts import TEXTS, BUTTONS, get_lang
from custom_filters import PrivateChatAndOwner
from start import admin_command
from Config import Config
import models


async def admin_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndOwner().filter(update):
        lang = get_lang(update.effective_user.id)
        keyboard = build_admin_settings_keyboard(lang)
        keyboard.append(build_back_to_home_page_button(lang=lang, is_admin=True)[0])
        await update.callback_query.edit_message_text(
            text=TEXTS[lang]["admin_settings_title"],
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return ConversationHandler.END


admin_settings_handler = CallbackQueryHandler(
    admin_settings,
    "^admin_settings$|^back_to_admin_settings$",
)


NEW_ADMIN_ID, SELECT_PERMISSIONS = range(2)


async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndOwner().filter(update):
        lang = get_lang(update.effective_user.id)
        await update.callback_query.answer()
        await update.callback_query.delete_message()
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=TEXTS[lang]["add_admin_instruction"],
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(
                            text=BUTTONS[lang]["select_admin_button"],
                            request_users=KeyboardButtonRequestUsers(
                                request_id=4, user_is_bot=False
                            ),
                        )
                    ]
                ],
                resize_keyboard=True,
            ),
        )
        return NEW_ADMIN_ID


async def get_new_admin_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndOwner().filter(update):
        lang = get_lang(update.effective_user.id)
        if update.effective_message.users_shared:
            admin_id = update.effective_message.users_shared.users[0].user_id
        else:
            admin_id = int(update.message.text)

        try:
            await context.bot.get_chat(chat_id=admin_id)
        except:
            await update.message.reply_text(text=TEXTS[lang]["user_not_found"])
            return

        context.user_data["new_admin_id"] = admin_id

        selected_permissions = set()

        with models.session_scope() as s:
            admin_permissions = (
                s.query(models.AdminPermission)
                .filter(models.AdminPermission.admin_id == admin_id)
                .all()
            )
            for admin_permission in admin_permissions:
                selected_permissions.add(admin_permission.permission)

        context.user_data["selected_permissions"] = selected_permissions

        permissions_keyboard = build_permissions_keyboard(lang, selected_permissions)
        permissions_keyboard.append(
            [
                InlineKeyboardButton(
                    text=BUTTONS[lang]["skip_button"],
                    callback_data="skip_permissions",
                )
            ]
        )
        permissions_keyboard.append(
            build_back_button("back_to_get_new_admin_id", lang=lang)
        )
        permissions_keyboard.append(
            build_back_to_home_page_button(lang=lang, is_admin=True)[0]
        )

        await update.message.reply_text(
            text=TEXTS[lang]["user_found"],
            reply_markup=ReplyKeyboardRemove(),
        )
        await update.message.reply_text(
            text=TEXTS[lang]["select_permissions_instruction"],
            reply_markup=InlineKeyboardMarkup(permissions_keyboard),
        )
        return SELECT_PERMISSIONS


back_to_get_new_admin_id = add_admin


async def toggle_permission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndOwner().filter(update):
        lang = get_lang(update.effective_user.id)
        callback_data = update.callback_query.data

        permission_str = callback_data.replace("toggle_permission_", "")
        try:
            permission = models.Permission(permission_str)
        except ValueError:
            await update.callback_query.answer(
                text="Invalid permission", show_alert=True
            )
            return

        selected_permissions = context.user_data.get("selected_permissions", set())

        if permission in selected_permissions:
            selected_permissions.remove(permission)
        else:
            selected_permissions.add(permission)

        context.user_data["selected_permissions"] = selected_permissions

        permissions_keyboard = build_permissions_keyboard(lang, selected_permissions)
        permissions_keyboard.append(
            [
                InlineKeyboardButton(
                    text=BUTTONS[lang]["save_button"],
                    callback_data="save_permissions",
                )
            ]
        )
        permissions_keyboard.append(
            build_back_button("back_to_get_new_admin_id", lang=lang)
        )
        permissions_keyboard.append(
            build_back_to_home_page_button(lang=lang, is_admin=True)[0]
        )

        await update.callback_query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(permissions_keyboard)
        )


async def skip_or_save_permissions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndOwner().filter(update):
        lang = get_lang(update.effective_user.id)
        admin_id = context.user_data.get("new_admin_id")
        selected_permissions = context.user_data.get("selected_permissions", set())

        if admin_id:
            with models.session_scope() as s:
                admin = s.get(models.User, admin_id)

                if not admin:
                    admin_chat = await context.bot.get_chat(chat_id=admin_id)
                    admin = models.User(
                        user_id=admin_chat.id,
                        username=admin_chat.username if admin_chat.username else "",
                        name=admin_chat.full_name,
                        is_admin=True,
                    )
                    s.add(admin)

                admin.is_admin = True

                for permission in selected_permissions:
                    admin_permission = models.AdminPermission(
                        admin_id=admin_id, permission=permission
                    )
                    s.add(admin_permission)
                s.commit()
        await update.callback_query.answer(
            text=TEXTS[lang]["admin_added_success"],
            show_alert=True,
        )
        await update.callback_query.edit_message_text(
            text=TEXTS[lang]["home_page"],
            reply_markup=build_admin_keyboard(lang, update.effective_user.id),
        )
        return ConversationHandler.END


add_admin_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=add_admin,
            pattern="^add_admin$",
        ),
    ],
    states={
        NEW_ADMIN_ID: [
            MessageHandler(
                filters=filters.Regex("^\d+$") | filters.StatusUpdate.USERS_SHARED,
                callback=get_new_admin_id,
            ),
        ],
        SELECT_PERMISSIONS: [
            CallbackQueryHandler(
                callback=toggle_permission,
                pattern=r"^toggle_permission_[^_]+$",
            ),
            CallbackQueryHandler(
                callback=skip_or_save_permissions,
                pattern="^((skip)|(save))_permissions$",
            ),
        ],
    },
    fallbacks=[
        admin_settings_handler,
        admin_command,
        back_to_admin_home_page_handler,
        CallbackQueryHandler(
            back_to_get_new_admin_id, pattern=r"^back_to_get_new_admin_id$"
        ),
    ],
)


CHOOSE_ADMIN_ID_TO_REMOVE = range(1)


async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndOwner().filter(update):
        lang = get_lang(update.effective_user.id)
        with models.session_scope() as s:

            if update.callback_query.data.isnumeric():
                admin = s.get(models.User, int(update.callback_query.data))

                if admin.user_id == Config.OWNER_ID:
                    await update.callback_query.answer(
                        text=TEXTS[lang]["cannot_remove_owner"],
                        show_alert=True,
                    )
                    return
                admin.is_admin = False
                s.query(models.AdminPermission).filter(
                    models.AdminPermission.admin_id == admin.user_id
                ).delete()
                s.commit()
                await update.callback_query.answer(
                    text=TEXTS[lang]["admin_removed_success"],
                    show_alert=True,
                )

            await update.callback_query.answer()
            admins = s.query(models.User).filter(models.User.is_admin == True).all()
            admin_ids_keyboard = [
                [
                    InlineKeyboardButton(
                        text=admin.name,
                        callback_data=str(admin.user_id),
                    ),
                ]
                for admin in admins
            ]
        admin_ids_keyboard.append(
            build_back_button("back_to_admin_settings", lang=lang)
        )
        admin_ids_keyboard.append(
            build_back_to_home_page_button(lang=lang, is_admin=True)[0]
        )
        await update.callback_query.edit_message_text(
            text=TEXTS[lang]["remove_admin_instruction"],
            reply_markup=InlineKeyboardMarkup(admin_ids_keyboard),
        )
        return CHOOSE_ADMIN_ID_TO_REMOVE


remove_admin_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=remove_admin,
            pattern="^remove_admin$",
        ),
    ],
    states={
        CHOOSE_ADMIN_ID_TO_REMOVE: [
            CallbackQueryHandler(
                remove_admin,
                "^\d+$",
            ),
        ]
    },
    fallbacks=[
        admin_settings_handler,
        admin_command,
        back_to_admin_home_page_handler,
    ],
)


async def show_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndOwner().filter(update):
        lang = get_lang(update.effective_user.id)
        with models.session_scope() as s:
            admins = s.query(models.User).filter(models.User.is_admin == True).all()
            text = ""
            for admin in admins:
                if admin.user_id == Config.OWNER_ID:
                    text += f"<b>{TEXTS[lang]['bot_owner']}</b>\n" + str(admin) + "\n\n"
                    continue
                text += str(admin) + "\n\n"
        text += TEXTS[lang]["continue_with_admin_command"]
        await update.callback_query.edit_message_text(text=text)


show_admins_handler = CallbackQueryHandler(
    callback=show_admins,
    pattern="^show_admins$",
)


CHOOSE_ADMIN_TO_EDIT_PERMISSIONS, EDITING_PERMISSIONS = range(2)


async def edit_admin_permissions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndOwner().filter(update):
        lang = get_lang(update.effective_user.id)
        with models.session_scope() as s:
            admins = (
                s.query(models.User)
                .filter(
                    sa.and_(
                        models.User.is_admin == True,
                        models.User.user_id != Config.OWNER_ID,
                    )
                )
                .all()
            )

            if not admins:
                await update.callback_query.answer(
                    text=TEXTS[lang]["no_admins_to_edit"], show_alert=True
                )
                return ConversationHandler.END

            admin_keyboard = build_keyboard(
                columns=1,
                texts=[admin.name for admin in admins],
                buttons_data=[str(admin.user_id) for admin in admins],
            )
            admin_keyboard.append(
                build_back_button("back_to_admin_settings", lang=lang)
            )
            admin_keyboard.append(
                build_back_to_home_page_button(lang=lang, is_admin=True)[0]
            )

            await update.callback_query.edit_message_text(
                text=TEXTS[lang]["select_admin_to_edit_permissions"],
                reply_markup=InlineKeyboardMarkup(admin_keyboard),
            )
        return CHOOSE_ADMIN_TO_EDIT_PERMISSIONS


async def show_admin_permissions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndOwner().filter(update):
        lang = get_lang(update.effective_user.id)
        admin_id = int(update.callback_query.data)

        if admin_id == Config.OWNER_ID:
            await update.callback_query.answer(
                text=TEXTS[lang]["cannot_edit_owner_permissions"], show_alert=True
            )
            return

        with models.session_scope() as s:
            admin = s.get(models.User, admin_id)
            current_permissions = (
                s.query(models.AdminPermission)
                .filter(models.AdminPermission.admin_id == admin_id)
                .all()
            )
            selected_permissions = {perm.permission for perm in current_permissions}

        context.user_data["editing_admin_id"] = admin_id

        permissions_keyboard = build_permissions_keyboard(lang, selected_permissions)
        permissions_keyboard.append(
            build_back_button("back_to_choose_admin_permissions", lang=lang)
        )
        permissions_keyboard.append(
            build_back_to_home_page_button(lang=lang, is_admin=True)[0]
        )

        admin_info = f"<b>{admin.name}</b>\n{str(admin)}\n\n"
        permissions_text = TEXTS[lang]["current_permissions"] + "\n"

        if selected_permissions:
            permission_names = {
                models.Permission.BAN_USERS: TEXTS[lang].get(
                    "permission_ban_users", "Ban/Unban Users"
                ),
                models.Permission.BROADCAST: TEXTS[lang].get(
                    "permission_broadcast", "Broadcast Messages"
                ),
                models.Permission.MANAGE_FORCE_JOIN: TEXTS[lang].get(
                    "permission_manage_force_join", "Manage Force Join"
                ),
                models.Permission.VIEW_IDS: TEXTS[lang].get("permission_view_ids", "View IDs"),
            }
            for perm in selected_permissions:
                permissions_text += f"✅ {permission_names.get(perm, perm.value)}\n"
        else:
            permissions_text += TEXTS[lang]["no_permissions"]

        await update.callback_query.edit_message_text(
            text=(
                admin_info
                + permissions_text
                + "\n\n"
                + TEXTS[lang]["select_permissions_instruction"]
            ),
            reply_markup=InlineKeyboardMarkup(permissions_keyboard),
        )
        return EDITING_PERMISSIONS


back_to_choose_admin_permissions = edit_admin_permissions


async def toggle_admin_permission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndOwner().filter(update):
        lang = get_lang(update.effective_user.id)
        permission_str = update.callback_query.data.replace("toggle_permission_", "")
        admin_id = context.user_data["editing_admin_id"]

        if not admin_id or admin_id == Config.OWNER_ID:
            await update.callback_query.answer(
                text=TEXTS[lang]["cannot_edit_owner_permissions"], show_alert=True
            )
            return

        with models.session_scope() as s:
            existing = (
                s.query(models.AdminPermission)
                .filter(
                    models.AdminPermission.admin_id == admin_id,
                    models.AdminPermission.permission == models.Permission(permission_str),
                )
                .first()
            )

            if existing:
                s.delete(existing)
                message = TEXTS[lang]["permission_revoked"]
            else:
                new_permission = models.AdminPermission(
                    admin_id=admin_id, permission=models.Permission(permission_str)
                )
                s.add(new_permission)
                message = TEXTS[lang]["permission_granted"]

            s.commit()

            current_permissions = (
                s.query(models.AdminPermission)
                .filter(models.AdminPermission.admin_id == admin_id)
                .all()
            )
            selected_permissions = {perm.permission for perm in current_permissions}

        permissions_keyboard = build_permissions_keyboard(lang, selected_permissions)
        permissions_keyboard.append(
            build_back_button("back_to_choose_admin_permissions", lang=lang)
        )
        permissions_keyboard.append(
            build_back_to_home_page_button(lang=lang, is_admin=True)[0]
        )

        await update.callback_query.answer(text=message, show_alert=True)
        await update.callback_query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(permissions_keyboard)
        )


edit_admin_permissions_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=edit_admin_permissions,
            pattern="^edit_admin_permissions$",
        ),
    ],
    states={
        CHOOSE_ADMIN_TO_EDIT_PERMISSIONS: [
            CallbackQueryHandler(
                callback=show_admin_permissions,
                pattern=r"^[0-9]+$",
            ),
        ],
        EDITING_PERMISSIONS: [
            CallbackQueryHandler(
                callback=toggle_admin_permission,
                pattern=r"^toggle_permission_",
            ),
        ],
    },
    fallbacks=[
        admin_settings_handler,
        admin_command,
        back_to_admin_home_page_handler,
        CallbackQueryHandler(
            callback=back_to_choose_admin_permissions,
            pattern="^back_to_choose_admin_permissions$",
        ),
    ],
)
