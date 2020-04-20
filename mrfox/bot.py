import logging
import sys

from telegram import Bot
from telegram.utils.request import Request

from mrfox.db import DB, init_db
from mrfox.config import load_config


class MrFox(Bot):
    def __init__(self, config_path=None):
        conf = load_config(config_path)

        request = Request(con_pool_size=conf['CONNECTION_POOL_SIZE'])
        super().__init__(conf['TOKEN'], request=request)

        self.config = conf

        self.init_db()
        self.init_logging()

    def init_db(self):
        db = DB(self.config['DB_URI'])
        init_db(db)
        self.db = db

    def init_logging(self):
        logging.basicConfig(
            level=getattr(logging, self.config['LEVEL']),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            stream=sys.stdout
        )
