from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TimedOut, NetworkError
import traceback
import json
import html
from Config import Config


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    if isinstance(context.error, (TimedOut, NetworkError)):
        return
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    try:
        error = f"update = {json.dumps(update_str, indent=2, ensure_ascii=False)}\n\n"

    except TypeError:
        error = "update = TypeError\n\n"

    error += (
        f"user_data = {str(context.user_data)}\n"
        f"chat_data = {str(context.chat_data)}\n\n"
        f"{tb_string}\n\n"
    )

    write_error(error)

    await context.bot.send_message(
        chat_id=Config.ERRORS_CHANNEL,
        text=f"<pre>{html.escape(tb_string)}</pre>",
    )


def write_error(error: str):
    with open("errors.txt", "a", encoding="utf-8") as f:
        f.write(error + f"{'-'*100}\n\n\n")
