import traceback
from urllib.parse import urlparse

from telegram import MessageEntity
from telegram.ext import CommandHandler, MessageHandler, BaseFilter, Filters

from mrfox.db import Client
from mrfox.rutracker import RuTrackerError


class AuthFilter(BaseFilter):
    def __init__(self, bot):
        self.db = bot.db
        self.logger = bot.logger

    def filter(self, message):
        with self.db.session_scope() as session:
            client = session.query(Client).filter_by(
                external_id=message.from_user.id
            ).first()
            self.logger.debug('Client: %s', client)
            return bool(client)


def route_commands(updater):
    auth_filter = AuthFilter(updater.bot)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('ping', ping))

    url_handler = MessageHandler(
        auth_filter & Filters.text & (
            Filters.entity(MessageEntity.URL) | Filters.entity(MessageEntity.TEXT_LINK)
        ),
        url_message_handler
    )
    updater.dispatcher.add_handler(url_handler)

    updater.dispatcher.add_handler(MessageHandler(auth_filter, unknown_message))

    updater.dispatcher.add_error_handler(error_callback)


def start(update, context):
    if not context.args or context.args[0] != context.bot.config['PASSWORD']:
        return

    user = update.message.from_user

    with context.bot.db.session_scope() as session:
        client = session.query(Client).filter_by(external_id=user['id']).first()
        context.bot.logger.debug('Client: %s', client)
        if not client:
            client = Client(
                external_id=user['id'],
                first_name=user['first_name'],
                last_name=user['last_name'],
            )
            session.add(client)
            context.bot.logger.debug('Add new client: %s', client)

    update.message.reply_text(
        'Hello {}'.format(update.message.from_user.first_name))

    session.commit()


def ping(update, context):
    update.message.reply_text('pong')


def url_message_handler(update, context):
    url = update.message.text
    parsed = urlparse(url)
    bot = context.bot

    if 'rutracker' in parsed.netloc:
        try:
            filename, torrent = bot.rutracker.get_torrent_file(parsed)
            bot.torrent.add_rutracker_torrent(filename, torrent)
            update.message.reply_text("ok")
        except RuTrackerError as e:
            update.message.reply_text(str(e))
        return

    update.message.reply_text("I don't know what to do with this url")


def unknown_message(update, context):
    update.message.reply_text("I don't know what to do with it")


def error_callback(update, context):
    err = context.error
    tb = traceback.format_exception(type(err), err, err.__traceback__)
    context.bot.logger.error(
        "Some error: %s\nContext: %s\n\n%s",
        err, context.__dict__, ''.join(tb)
    )
