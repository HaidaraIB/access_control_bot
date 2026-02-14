from telegram import Message
from telegram.ext import ContextTypes


async def send_to(users: list[int], context: ContextTypes.DEFAULT_TYPE):
    msg: Message = context.user_data["the_message"]
    media_types = {
        "photo": msg.photo[-1] if msg.photo else None,
        "video": msg.video,
        "audio": msg.audio,
        "voice": msg.voice,
    }
    media = None
    media_type = None
    for m_type, m in media_types.items():
        if m:
            media = m
            media_type = m_type
            break

    for user in users:
        try:
            if media:
                send_func = getattr(context.bot, f"send_{media_type}")
                await send_func(
                    chat_id=user,
                    caption=msg.caption,
                    **{media_type: media},
                )
            else:
                await context.bot.send_message(chat_id=user, text=msg.text)
        except:
            continue
