import traceback

from telegram.ext import CommandHandler, MessageHandler, BaseFilter

from mrfox.db import Client


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


def unknown_message(update, context):
    update.message.reply_text("I don't know what to do with it")


def error_callback(update, context):
    err = context.error
    tb = traceback.format_exception(type(err), err, err.__traceback__)
    context.bot.logger.error(
        "Some error: %s\nContext: %s\n\n%s",
        err, context.__dict__, ''.join(tb)
    )
