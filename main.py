from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)
filterwarnings(
    action="ignore", message=r".*the `days` parameter.*", category=PTBUserWarning
)
filterwarnings(
    action="ignore", message=r".*invalid escape sequence.*", category=SyntaxWarning
)

import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

from handlers import setup_and_run

if __name__ == "__main__":
    setup_and_run()
