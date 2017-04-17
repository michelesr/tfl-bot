from telegram import ReplyKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler
import os
import datetime
import time
import sys
import logging
import _thread
import tfl

LOG_LEVEL = logging.DEBUG

POLL_INTERVAL = os.getenv('POLL_INTERVAL')
if POLL_INTERVAL:
    POLL_INTERVAL = float(POLL_INTERVAL)

TIMEOUT = os.getenv('TIMEOUT')
if TIMEOUT:
    TIMEOUT = float(TIMEOUT)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=LOG_LEVEL)
logger = logging.getLogger(__name__)

with open('./token', 'r') as f:
    TOKEN = f.read()


def filter_args(update):
    args = update.message.text.split(' ')
    return list(filter(lambda x: x != '', args))


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hello!')


def line_menu(bot, update):
    text = """
Which line? Some examples:
/line central
/line 12
/line london-overground
"""

    reply_keyboard = map(lambda x: ['/line ' + x['id']], tfl.get_lines('tube'))
    bot.sendMessage(
        update.message.chat_id,
        text=text,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True))


def modes(bot, update):
    mode_names = list(tfl.get_mode_names())
    text = """Available modes are: {}
Use /list <mode> to find the lines for a particular mode""".format(mode_names)
    reply_keyboard = map(lambda x: ['/list ' + x], mode_names)
    bot.sendMessage(
        update.message.chat_id,
        text=text,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True))


def list_lines(bot, update, args=None):
    if not args:
        return modes(bot, update)
    mode = args.pop()
    line_ids = list(map(lambda line: line['id'], tfl.get_lines(mode)))
    text = """Available lines for this mode are: {}
Use /line <line> to get the line status""".format(line_ids)

    if len(text) > 4000:
        text = text[:4000]
        reply_markup = None
        text = """Sorry, the list is too long to display.
For buses, try using /line with the bus number"""
        bot.sendMessage(update.message.chat_id, text=text)
    else:
        reply_keyboard = map(lambda x: ['/line ' + x], line_ids)
        reply_markup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True)
        bot.sendMessage(
            update.message.chat_id, text=text, reply_markup=reply_markup)


def line(bot, update, args=None):
    if not args:
        return line_menu(bot, update)
    for line in args:
        for message in tfl.format_status(tfl.get_line_status(line)):
            bot.sendMessage(
                update.message.chat_id,
                text=message,
                parse_mode=ParseMode.HTML)



# use this to fix restart loop if necessary
def check_timedelta(update):
    time = update.message.date
    now = datetime.datetime.now()
    delta = datetime.timedelta(seconds=5)
    return (now - time) < delta


def debug(bot, update, args=None):
    logger.debug('/debug handler called')
    # list of user ids allowed to use debug commands
    trusted_users = []
    trust = update.message.from_user.id in trusted_users
    if not trust or not args:
        return
    elif args[0] in ('restart'):
        sleep_time = 2
        logger.warn('Restarting in {} seconds'.format(sleep_time))
        time.sleep(sleep_time)
        os.execl(sys.executable, sys.executable, *sys.argv)

updater = Updater(token=TOKEN)
updater.dispatcher.add_handler(CommandHandler('line', line, pass_args=True))
updater.dispatcher.add_handler(
    CommandHandler('list', list_lines, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('modes', modes))
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(
    CommandHandler('debug', debug, pass_args=True))

updater.dispatcher.add_error_handler(error)
updater.start_polling(poll_interval=1.0, timeout=20)
updater.idle()
