import re
from logging import getLogger
from urllib.parse import ParseResult

from requests import Session, Response
from requests.exceptions import RequestException


logger = getLogger(__name__)


class RuTrackerError(Exception):
    pass


class RuTrackerAnswerError(RuTrackerError):
    def __init__(self, code, headers, body):
        super().__init__(
            "Bad answer:\n Code: %s\n Headers: %s\n Body: %s" % (
                code, headers, body,
            )
        )


class RuTracker(Session):
    def __init__(self, username: str, password: str):
        super().__init__()

        self.username = username
        self.password = password
        self.base_url = 'https://rutracker.org/forum/'
        self.torrent_url_pattern = re.compile(r".*t=\d+.*")

    def request(self, method: str, url: str, *args, **kwargs) -> Response:
        url = self.base_url + url
        try:
            res = super().request(method, url, *args, **kwargs)
            res.raise_for_status()
        except RequestException as e:
            raise RuTrackerError(e)
        return res

    def login(self) -> None:
        logger.info("Loggin on rutracker")
        url = 'login.php'
        data = {
            "login_username": self.username,
            "login_password": self.password,
            "login": "вход",
        }
        self.post(url, data)

    def get_torrent_file(self, url: ParseResult) -> (str, bytes):
        if not self.torrent_url_pattern.match(url.query):
            raise RuTrackerError("incorrect url")

        url = 'dl.php?' + url.query
        conn_close = {'Connection': 'close'}
        r = self.get(url, allow_redirects=False, headers=conn_close)
        if r.is_redirect and 'login' in r.headers['location']:
            self.login()
            r = self.get(url, allow_redirects=False, headers=conn_close)

        if r.status_code != 200:
            raise RuTrackerAnswerError(
                r.status_code, r.headers, r.text[:10]
            )

        filename = "unknown"
        parts = r.headers.get('Content-Disposition', "").split(";")
        for part in parts:
            if "filename" in part:
                s = part.split("=")
                if len(s) > 1:
                    filename = s[1]
                    break

        return filename, r.content
