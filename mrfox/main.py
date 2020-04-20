from telegram.ext import Updater

from mrfox.bot import MrFox
from mrfox.commands import route_commands


def main():
    updater = Updater(bot=MrFox(), use_context=True)
    route_commands(updater)
    updater.start_polling()
    updater.bot.logger.info('Starting bot')
    updater.idle()


if __name__ == '__main__':
    main()
