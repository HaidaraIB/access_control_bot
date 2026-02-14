import models

TEXTS = {
    models.Language.ARABIC: {
        "user_welcome_msg": "أهلاً بك...",
        "admin_welcome_msg": "أهلاً بك...",
        "force_join_msg": (
            f"لبدء استخدام البوت يجب عليك الانضمام الى محادثة البوت أولاً\n\n"
            "<b>اشترك أولاً 👇</b>\n"
            "ثم اضغط <b>تحقق ✅</b>"
        ),
        "force_join_multiple_msg": (
            f"لبدء استخدام البوت يجب عليك الانضمام الى محادثات البوت أولاً\n\n"
            "<b>اشترك في جميع المحادثات 👇</b>\n"
            "ثم اضغط <b>تحقق ✅</b>"
        ),
        "join_first_answer": "قم بالاشتراك بالمحادثة أولاً ❗️",
        "join_all_first_answer": "قم بالاشتراك في جميع المحادثات أولاً ❗️",
        "settings": "الإعدادات ⚙️",
        "change_lang": "اختر اللغة 🌐",
        "change_lang_success": "تم تغيير اللغة بنجاح ✅",
        "home_page": "القائمة الرئيسية 🔝",
        "currently_admin": "تعمل الآن كآدمن 🕹",
        "admin_settings_title": "إعدادات الآدمن 🪄",
        "add_admin_instruction": (
            "اختر حساب الآدمن الذي تريد إضافته بالضغط على الزر أدناه\n\n"
            "يمكنك إرسال الid برسالة أيضاً\n\n"
            "أو إلغاء العملية بالضغط على /admin."
        ),
        "admin_added_success": "تمت إضافة الآدمن بنجاح ✅",
        "cannot_remove_owner": "لا يمكنك إزالة مالك البوت من قائمة الآدمنز ❗️",
        "admin_removed_success": "تمت إزالة الآدمن بنجاح ✅",
        "remove_admin_instruction": "اختر من القائمة أدناه الآدمن الذي تريد إزالته.",
        "continue_with_admin_command": "للمتابعة اضغط /admin",
        "keyboard_hidden": "تم الإخفاء ✅",
        "keyboard_shown": "تم الإظهار ✅",
        "ban_instruction": (
            "اختر حساب المستخدم الذي تريد حظره بالضغط على الزر أدناه\n\n"
            "يمكنك إرسال الid برسالة أيضاً\n\n"
            "أو إلغاء العملية بالضغط على /admin."
        ),
        "user_not_found": (
            "لم يتم العثور على المستخدم ❌\n"
            "تأكد من الآيدي أو من أن المستخدم قد بدأ محادثة مع البوت من قبل"
        ),
        "user_found": "تم العثور على المستخدم ✅",
        "do_you_want": "هل تريد",
        "operation_success": "تمت العملية بنجاح ✅",
        "ban_confirmation": (
            "معلومات المستخدم:\n"
            "{user_info}\n\n"
            "حالة الحظر الحالية: <b>{ban_status}</b>\n\n"
            "سيتم <b>{action}</b> هذا المستخدم.\n\n"
            "اضغط على زر <b>تأكيد</b> للمتابعة."
        ),
        "user_banned": "محظور 🔒",
        "user_not_banned": "غير محظور 🔓",
        "action_ban": "حظر",
        "action_unban": "فك حظر",
        "send_message": "أرسل الرسالة",
        "send_message_to": "هل تريد إرسال الرسالة إلى:",
        "send_user_ids": "قم بإرسال آيديات المستخدمين الذين تريد إرسال الرسالة لهم سطراً سطراً.",
        "send_chat_id": "أرسل آيدي القناة/المجموعة",
        "sending_messages": "يقوم البوت بإرسال الرسائل الآن، يمكنك متابعة استخدامه بشكل طبيعي",
        "bot_must_be_member": "يجب أن يكون البوت مشتركاً في هذه القناة/المجموعة حتى يتمكن من النشر فيها",
        "message_published_success": "تم نشر الرسالة في {chat_title} بنجاح ✅",
        "bot_owner": "مالك البوت",
        "force_join_chats_title": "إدارة محادثات الإجبار على الانضمام 💬",
        "add_force_join_chat_instruction": (
            "اختر المحادثة التي تريد إجبار المستخدمين على الانضمام إليها بالضغط على الزر أدناه\n\n"
            "يمكنك إرسال الid برسالة أيضاً\n\n"
            "أو إلغاء العملية بالضغط على /admin."
        ),
        "enter_chat_link_instruction": (
            "تم العثور على المحادثة: <b>{chat_title}</b>\n\n"
            "أرسل رابط المحادثة (invite link) أو اسم المستخدم\n\n"
            "مثال: https://t.me/channel_name أو @channel_name"
        ),
        "force_join_chat_added_success": "تمت إضافة محادثة الإجبار على الانضمام بنجاح ✅",
        "force_join_chat_removed_success": "تمت إزالة محادثة الإجبار على الانضمام بنجاح ✅",
        "remove_force_join_chat_instruction": "اختر من القائمة أدناه المحادثة التي تريد إزالتها.",
        "no_force_join_chats": "لا توجد محادثات إجبار على الانضمام حالياً ❗️",
        "force_join_chats_list_title": "قائمة محادثات الإجبار على الانضمام:",
        "invalid_chat_id": "آيدي المحادثة غير صحيح ❌",
        "chat_not_found": "لم يتم العثور على المحادثة ❌\nتأكد من الآيدي أو من أن البوت عضو في المحادثة",
        "chat_link_required": "المحادثة لا تحتوي على رابط دعوة. يرجى إرسال رابط الدعوة يدوياً.",
        "invalid_chat_link": "رابط المحادثة غير صحيح ❌\nيجب أن يبدأ بـ https://t.me/ أو @",
        "select_permissions_instruction": "اختر الصلاحيات التي تريد منحها لهذا الآدمن:",
        "permissions_selected": "تم اختيار الصلاحيات بنجاح ✅",
        "manage_permissions": "إدارة الصلاحيات 🔐",
        "edit_admin_permissions": "تعديل صلاحيات الآدمن 🔐",
        "select_admin_to_edit_permissions": "اختر الآدمن الذي تريد تعديل صلاحياته:",
        "current_permissions": "الصلاحيات الحالية:",
        "no_permissions": "لا توجد صلاحيات",
        "permission_granted": "تم منح الصلاحية ✅",
        "permission_revoked": "تم سحب الصلاحية ✅",
        "cannot_edit_owner_permissions": "لا يمكنك تعديل صلاحيات مالك البوت ❗️",
        "permission_ban_users": "حظر/فك حظر المستخدمين",
        "permission_broadcast": "إرسال رسائل جماعية",
        "permission_manage_force_join": "إدارة محادثات الإجبار على الانضمام",
        "permission_view_ids": "عرض معرفات المستخدمين/المحادثات",
        "permission_manage_permissions": "إدارة الصلاحيات",
        "permission_manage_admins": "إدارة الآدمنز",
        "toggle_permission": "تبديل الصلاحية",
        "all_permissions": "جميع الصلاحيات",
        "no_permissions_selected": "لم يتم اختيار أي صلاحيات",
        "no_admins_to_edit": "لا يوجد أدمنز لتعديل صلاحياتهم",
        "you_dont_have_permission_to_manage_permissions": "لا يمكنك تعديل صلاحيات الآدمنز",
        "you_dont_have_permission_to_manage_admins": "لا يمكنك تعديل صلاحيات الآدمنز",
        "you_dont_have_permission_to_ban_users": "لا يمكنك تعديل صلاحيات الآدمنز",
        "you_dont_have_permission_to_broadcast": "لا يمكنك تعديل صلاحيات الآدمنز",
        "you_dont_have_permission_to_manage_force_join": "لا يمكنك تعديل صلاحيات الآدمنز",
        "you_dont_have_permission_to_view_ids": "لا يمكنك تعديل صلاحيات الآدمنز",
        "manage_users_settings_title": "إدارة المستخدمين 👥",
        "export_users_to_excel": "تصدير المستخدمين إلى Excel 📊",
        "exporting_users": "جاري تصدير المستخدمين...",
        "users_exported_success": "تم تصدير المستخدمين بنجاح ✅",
        "export_error": "حدث خطأ أثناء التصدير ❌",
        "excel_user_id": "معرف المستخدم",
        "excel_username": "اسم المستخدم",
        "excel_name": "الاسم",
        "excel_language": "اللغة",
        "excel_is_admin": "آدمن",
        "excel_is_banned": "محظور",
        "excel_created_at": "تاريخ الإنشاء",
        "excel_no_username": "غير متوفر",
        "excel_unknown": "غير معروف",
        "excel_yes": "نعم",
        "excel_no": "لا",
        "lang_arabic": "العربية",
        "lang_english": "English",
    },
    models.Language.ENGLISH: {
        "user_welcome_msg": "Welcome...",
        "admin_welcome_msg": "Welcome...",
        "force_join_msg": (
            f"You have to join the bot's chat in order to be able to use it\n\n"
            "<b>Join First 👇</b>\n"
            "And then press <b>Verify ✅</b>"
        ),
        "force_join_multiple_msg": (
            f"You have to join the bot's chats in order to be able to use it\n\n"
            "<b>Join all chats 👇</b>\n"
            "And then press <b>Verify ✅</b>"
        ),
        "join_first_answer": "Join the chat first ❗️",
        "join_all_first_answer": "Join all chats first ❗️",
        "settings": "Settings ⚙️",
        "change_lang": "Choose a language 🌐",
        "change_lang_success": "Language changed ✅",
        "home_page": "Home page 🔝",
        "currently_admin": "You're currently an Admin 🕹",
        "admin_settings_title": "Admin Settings 🪄",
        "add_admin_instruction": (
            "Choose the admin account you want to add by clicking the button below\n\n"
            "You can also send the ID in a message\n\n"
            "Or cancel the operation by pressing /admin."
        ),
        "admin_added_success": "Admin added successfully ✅",
        "cannot_remove_owner": "You cannot remove the bot owner from the admin list ❗️",
        "admin_removed_success": "Admin removed successfully ✅",
        "remove_admin_instruction": "Choose from the list below the admin you want to remove.",
        "continue_with_admin_command": "To continue press /admin",
        "keyboard_hidden": "Hidden ✅",
        "keyboard_shown": "Shown ✅",
        "ban_instruction": (
            "Choose the user account you want to ban by clicking the button below\n\n"
            "You can also send the ID in a message\n\n"
            "Or cancel the operation by pressing /admin."
        ),
        "user_not_found": (
            "User not found ❌\n"
            "Make sure of the ID or that the user has started a conversation with the bot before"
        ),
        "user_found": "User found ✅",
        "do_you_want": "Do you want to",
        "operation_success": "Operation completed successfully ✅",
        "ban_confirmation": (
            "User Information:\n"
            "{user_info}\n\n"
            "Current Ban Status: <b>{ban_status}</b>\n\n"
            "This user will be <b>{action}</b>.\n\n"
            "Press the <b>Confirm</b> button to proceed."
        ),
        "user_banned": "Banned 🔒",
        "user_not_banned": "Not Banned 🔓",
        "action_ban": "ban",
        "action_unban": "unban",
        "send_message": "Send the message",
        "send_message_to": "Who do you want to send the message to:",
        "send_user_ids": "Send the user IDs you want to send the message to, one per line.",
        "send_chat_id": "Send the channel/group ID",
        "sending_messages": "The bot is sending messages now, you can continue using it normally",
        "bot_must_be_member": "The bot must be a member of this channel/group to be able to post in it",
        "message_published_success": "Message published in {chat_title} successfully ✅",
        "bot_owner": "Bot Owner",
        "force_join_chats_title": "Manage Force Join Chats 💬",
        "add_force_join_chat_instruction": (
            "Choose the chat you want to force users to join by clicking the button below\n\n"
            "You can also send the ID in a message\n\n"
            "Or cancel the operation by pressing /admin."
        ),
        "enter_chat_link_instruction": (
            "Chat found: <b>{chat_title}</b>\n\n"
            "Send the chat invite link or username\n\n"
            "Example: https://t.me/channel_name or @channel_name"
        ),
        "force_join_chat_added_success": "Force join chat added successfully ✅",
        "force_join_chat_removed_success": "Force join chat removed successfully ✅",
        "remove_force_join_chat_instruction": "Choose from the list below the chat you want to remove.",
        "no_force_join_chats": "No force join chats currently ❗️",
        "force_join_chats_list_title": "Force Join Chats List:",
        "invalid_chat_id": "Invalid chat ID ❌",
        "chat_not_found": "Chat not found ❌\nMake sure of the ID or that the bot is a member of the chat",
        "chat_link_required": "The chat doesn't have an invite link. Please send the invite link manually.",
        "invalid_chat_link": "Invalid chat link ❌\nMust start with https://t.me/ or @",
        "select_permissions_instruction": "Select the permissions you want to grant to this admin:",
        "permissions_selected": "Permissions selected successfully ✅",
        "manage_permissions": "Manage Permissions 🔐",
        "edit_admin_permissions": "Edit Admin Permissions 🔐",
        "select_admin_to_edit_permissions": "Select the admin whose permissions you want to edit:",
        "current_permissions": "Current Permissions:",
        "no_permissions": "No permissions",
        "permission_granted": "Permission granted ✅",
        "permission_revoked": "Permission revoked ✅",
        "cannot_edit_owner_permissions": "You cannot edit the bot owner's permissions ❗️",
        "permission_ban_users": "Ban/Unban Users",
        "permission_broadcast": "Broadcast Messages",
        "permission_manage_force_join": "Manage Force Join Chats",
        "permission_view_ids": "View User/Chat IDs",
        "permission_manage_permissions": "Manage Permissions",
        "permission_manage_admins": "Manage Admins",
        "toggle_permission": "Toggle Permission",
        "all_permissions": "All Permissions",
        "no_permissions_selected": "No permissions selected",
        "no_admins_to_edit": "No admins to edit permissions",
        "you_dont_have_permission_to_manage_permissions": "You don't have permission to manage permissions",
        "you_dont_have_permission_to_manage_admins": "You don't have permission to manage admins",
        "you_dont_have_permission_to_ban_users": "You don't have permission to ban users",
        "you_dont_have_permission_to_broadcast": "You don't have permission to broadcast",
        "you_dont_have_permission_to_manage_force_join": "You don't have permission to manage force join chats",
        "you_dont_have_permission_to_view_ids": "You don't have permission to view user/chat IDs",
        "manage_users_settings_title": "Manage Users 👥",
        "export_users_to_excel": "Export Users to Excel 📊",
        "exporting_users": "Exporting users...",
        "users_exported_success": "Users exported successfully ✅",
        "export_error": "An error occurred while exporting ❌",
        "excel_user_id": "User ID",
        "excel_username": "Username",
        "excel_name": "Name",
        "excel_language": "Language",
        "excel_is_admin": "Is Admin",
        "excel_is_banned": "Is Banned",
        "excel_created_at": "Created At",
        "excel_no_username": "N/A",
        "excel_unknown": "Unknown",
        "excel_yes": "Yes",
        "excel_no": "No",
        "lang_arabic": "Arabic",
        "lang_english": "English",
    },
}

BUTTONS = {
    models.Language.ARABIC: {
        "check_joined": "تحقق ✅",
        "bot_channel": "قناة البوت 📢",
        "bot_chat": "محادثة البوت 💬",
        "back_button": "الرجوع 🔙",
        "settings": "الإعدادات ⚙️",
        "lang": "اللغة 🌐",
        "back_to_home_page": "العودة إلى القائمة الرئيسية 🔙",
        "select_admin_button": "اختيار حساب آدمن",
        "select_user_button": "اختيار حساب مستخدم",
        "unban_button": "فك الحظر 🔓",
        "ban_button": "حظر 🔒",
        "add_admin": "إضافة آدمن ➕",
        "remove_admin": "حذف آدمن ✖️",
        "show_admins": "عرض الآدمنز الحاليين 👓",
        "admin_settings": "إعدادات الآدمن 🎛",
        "ban_unban": "حظر/فك حظر 🔓🔒",
        "hide_ids_keyboard": "إخفاء/إظهار كيبورد معرفة الآيديات🪄",
        "broadcast": "رسالة جماعية 👥",
        "everyone": "الجميع 👥",
        "specific_users": "مستخدمين محددين 👤",
        "all_users": "جميع المستخدمين 👨🏻‍💼",
        "all_admins": "جميع الآدمنز 🤵🏻",
        "channel_or_group": "قناة أو مجموعة 📢",
        "force_join_chats": "محادثات الإجبار على الانضمام 💬",
        "force_join_chats_settings": "إعدادات محادثات الإجبار على الانضمام 💬",
        "add_force_join_chat": "إضافة محادثة ➕",
        "remove_force_join_chat": "حذف محادثة ✖️",
        "show_force_join_chats": "عرض المحادثات 👓",
        "select_chat_button": "اختيار محادثة",
        "confirm_button": "تأكيد ✅",
        "bot": "بوت 🤖",
        "channel": "قناة 📢",
        "group": "مجموعة 👥",
        "user": "مستخدم 🆔",
        "manage_permissions": "إدارة الصلاحيات 🔐",
        "edit_permissions": "تعديل الصلاحيات ✏️",
        "skip_button": "تخطي ⬅️",
        "save_button": "حفظ ✅",
        "permission_ban_users": "حظر/فك حظر المستخدمين",
        "permission_broadcast": "إرسال رسائل جماعية",
        "permission_manage_force_join": "إدارة محادثات الإجبار على الانضمام",
        "permission_view_ids": "عرض معرفات المستخدمين/المحادثات",
        "permission_manage_permissions": "إدارة الصلاحيات",
        "permission_manage_admins": "إدارة الآدمنز",
        "manage_users_settings": "إدارة المستخدمين 👥",
        "export_users_to_excel": "تصدير المستخدمين إلى Excel 📊",
    },
    models.Language.ENGLISH: {
        "check_joined": "Verify ✅",
        "bot_channel": "Bot's Channel 📢",
        "bot_chat": "Bot's Chat 💬",
        "back_button": "Back 🔙",
        "settings": "Settings ⚙️",
        "lang": "Language 🌐",
        "back_to_home_page": "Back to home page 🔙",
        "select_admin_button": "Select Admin Account",
        "select_user_button": "Select User Account",
        "unban_button": "Unban 🔓",
        "ban_button": "Ban 🔒",
        "add_admin": "Add Admin ➕",
        "remove_admin": "Remove Admin ✖️",
        "show_admins": "Show Current Admins 👓",
        "admin_settings": "Admin Settings 🎛",
        "ban_unban": "Ban/Unban 🔓🔒",
        "hide_ids_keyboard": "Hide/Show ID Keyboard🪄",
        "broadcast": "Broadcast Message 👥",
        "everyone": "Everyone 👥",
        "specific_users": "Specific Users 👤",
        "all_users": "All Users 👨🏻‍💼",
        "all_admins": "All Admins 🤵🏻",
        "channel_or_group": "Channel or Group 📢",
        "force_join_chats": "Force Join Chats 💬",
        "force_join_chats_settings": "Force Join Chats Settings 💬",
        "add_force_join_chat": "Add Chat ➕",
        "remove_force_join_chat": "Remove Chat ✖️",
        "show_force_join_chats": "Show Chats 👓",
        "select_chat_button": "Select Chat",
        "confirm_button": "Confirm ✅",
        "bot": "Bot 🤖",
        "channel": "Channel 📢",
        "group": "Group 👥",
        "user": "User 🆔",
        "manage_permissions": "Manage Permissions 🔐",
        "edit_permissions": "Edit Permissions ✏️",
        "skip_button": "Skip ⬅️",
        "save_button": "Save ✅",
        "permission_ban_users": "Ban/Unban Users",
        "permission_broadcast": "Broadcast Messages",
        "permission_manage_force_join": "Manage Force Join Chats",
        "permission_view_ids": "View User/Chat IDs",
        "permission_manage_permissions": "Manage Permissions",
        "permission_manage_admins": "Manage Admins",
        "manage_users_settings": "Manage Users 👥",
        "export_users_to_excel": "Export Users to Excel 📊",
    },
}


def get_lang(user_id: int):
    with models.session_scope() as s:
        return s.get(models.User, user_id).lang
