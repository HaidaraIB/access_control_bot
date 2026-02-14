from pyrogram import Client
from Config import Config


class PyroClientSingleton(Client):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:

            cls._instance = Client(
                name="pyro_client",
                api_id=Config.API_ID,
                api_hash=Config.API_HASH,
                bot_token=Config.BOT_TOKEN,
            )
        return cls._instance
