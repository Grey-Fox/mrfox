import logging
import sys

from telegram import Bot
from telegram.utils.request import Request

from mrfox.db import DB, init_db
from mrfox.config import load_config
from mrfox.rutracker import RuTracker
from mrfox.torrent import Torrent


class MrFox(Bot):
    def __init__(self, config_path=None):
        conf = load_config(config_path)

        request = Request(con_pool_size=conf['CONNECTION_POOL_SIZE'])
        super().__init__(conf['TOKEN'], request=request)

        self.config = conf

        self.init_db()
        self.init_logging()
        self.init_rutracker()
        self.init_torrent()

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

    def init_rutracker(self):
        self.rutracker = RuTracker(
            username=self.config['RUTRACKER_LOGIN'],
            password=self.config['RUTRACKER_PASSWORD'],
        )

    def init_torrent(self):
        self.torrent = Torrent(
            host=self.config['DELUGE_HOST'],
            port=self.config['DELUGE_PORT'],
            user=self.config['DELUGE_USER'],
            password=self.config['DELUGE_PASSWORD'],
        )
