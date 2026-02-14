from telegram.ext import (
    ApplicationBuilder,
    Defaults,
    PicklePersistence,
)
from telegram.constants import ParseMode
from ptbcontrib.ptb_jobstores.sqlalchemy import PTBSQLAlchemyJobStore

from start import inits
from Config import Config


class MyApp:
    @classmethod
    def build_app(cls):
        defaults = Defaults(parse_mode=ParseMode.HTML)
        my_persistence = PicklePersistence(
            filepath="data/persistence", single_file=False
        )
        app = (
            ApplicationBuilder()
            .token(Config.BOT_TOKEN)
            .post_init(inits)
            .persistence(persistence=my_persistence)
            .defaults(defaults)
            .concurrent_updates(True)
            .build()
        )
        app.job_queue.scheduler.add_jobstore(
            PTBSQLAlchemyJobStore(
                application=app,
                url="sqlite:///data/jobs.sqlite3",
            )
        )
        return app
