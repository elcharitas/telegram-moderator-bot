#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Example Bot to moderate to Telegram group messages.

Run as:

MODERATOR_BOT_TOKEN=MYTOKEN python moderator.py

First, get the auth token for the bot.
Talk to @BotFather to do that.
See: https://core.telegram.org/bots#6-botfather

Now add the bot to the group and make it admin.
How to add bot to group: https://stackoverflow.com/questions/37338101
Note: to get all messages in the group, also need to set bot privacy
      mode to 'Disabled' (via @BotFather).

See: https://stackoverflow.com/questions/38565952
Bot also needs to be admin, check the group settings (pencil icon at the top).

Other references:
 http://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.html
 https://core.telegram.org/bots/api#available-methods
"""

import os
from telegram.ext import Updater, MessageHandler, Filters
import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

DISALLOWED_WORDS = set(['bad', 'sad', 'mad'])


def is_text_bad(text):
    words = set(text.lower().split())
    if words & DISALLOWED_WORDS:
        return True
    return False


def moderate(bot, update):
    """Moderate the user message."""
    if not update.message:
        return
    if is_text_bad(update.message.text):
        bot.delete_message(
            chat_id=update.message.chat_id,
            message_id=update.message.message_id)
        bot.send_message(
            chat_id=update.message.chat_id,
            text='What a shame, {}, I had to delete your message.'.format(
                update.message.from_user.first_name)
        )
        # Uncomment this to also kick the user from the group:
        # bot.kick_chat_member(
        #     chat_id=update.message.chat_id,
        #     user_id=update.message.from_user.id
        # )


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    token = os.getenv('MODERATOR_BOT_TOKEN')
    if not token:
        print(
            'MODERATOR_BOT_TOKEN environment variable not found.')
        return

    updater = Updater(token)
    dp = updater.dispatcher

    # Listen for messages and moderate them.
    dp.add_handler(MessageHandler(Filters.text, moderate))

    # Send all errors to the logger.
    dp.add_error_handler(error)

    updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
