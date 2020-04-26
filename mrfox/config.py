import os
from json import load

from dotenv import load_dotenv

DEFAULT_CONF = {
    'DB_URI': '/var/lib/mrfox',
    'TOKEN': None,
    'PASSWORD': None,
    'CONNECTION_POOL_SIZE': 10,
    'LEVEL': 'INFO',
    'RUTRACKER_LOGIN': None,
    'RUTRACKER_PASSWORD': None,

    'DELUGE_HOST': None,
    'DELUGE_PORT': 58846,
    'DELUGE_USER': None,
    'DELUGE_PASSWORD': None,
}

REQUIRED = (
    'TOKEN', 'PASSWORD', 'RUTRACKER_LOGIN', 'RUTRACKER_PASSWORD',
    'DELUGE_HOST', 'DELUGE_PORT', 'DELUGE_USER', 'DELUGE_PASSWORD',
)


def load_config(conf_path):
    conf = DEFAULT_CONF.copy()

    if conf_path:
        # load from json
        json_conf = load(open(conf_path, 'r'))
        if isinstance(json_conf, dict):
            conf.update(json_conf)

    # overwrite from env
    load_dotenv()
    for key in conf.keys():
        value = os.getenv('MRFOX_' + key)
        if value:
            conf[key] = value

    for key in REQUIRED:
        assert conf[key] is not None, 'specify {}'.format(key)
    return conf
