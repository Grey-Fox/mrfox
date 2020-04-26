from base64 import b64encode
from logging import getLogger

from deluge_client import DelugeRPCClient

logger = getLogger(__name__)


class Torrent(object):
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def add_rutracker_torrent(self, filename: str, torrent: bytes) -> None:
        logger.info("Add torrent")

        client = DelugeRPCClient(
            self.host,
            self.port,
            self.user,
            self.password,
        )
        client.call(
            'core.add_torrent_file', filename, b64encode(torrent), {}
        )
