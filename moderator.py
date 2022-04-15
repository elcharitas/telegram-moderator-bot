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
from profanity import profanity
from deep_translator import GoogleTranslator
import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


DISALLOWED_WORDS = {'scam', 'signup here', 'join my group', 'register and get', 'Sign up'}


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    token = os.getenv('MODERATOR_BOT_TOKEN')
    if not token:
        print(
            'MODERATOR_BOT_TOKEN environment variable not found.')
        return

    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    # translator = Translator()
    
    def is_text_bad(text):
        text = GoogleTranslator('auto','en').translate(text)
        words = set(text.lower().split())
        if words & DISALLOWED_WORDS:
            return True
        return profanity.contains_profanity(text) or False

    def moderate(update, context):
        """Moderate the user message."""
        try:
            if is_text_bad(update.message.text):
                user_id = update.message.from_user.id
                chat_id = update.message.chat_id
                if updater.bot.get_chat_member(chat_id, user_id).status == 'member':
                    updater.bot.delete_message(
                        chat_id=chat_id,
                        message_id=update.message.message_id)
                    updater.bot.send_message(
                        chat_id=chat_id,
                        text=f'What a shame, {update.message.from_user.first_name}, I had to delete your message. It violates our community rules.',
                    )
                    context.user_data[user_id] += 1
                    # Uncomment this to also kick the user from the group:
                    if context.user_data[user_id] > 3:
                        updater.bot.kick_chat_member(
                            chat_id=chat_id,
                            user_id=user_id
                        )
                        updater.bot.send_message(
                            chat_id=chat_id,
                            text=f'@{update.message.from_user.username} has been removed for violating rules!',
                        )
            elif update.message.text.endswith('joined the group'):
                updater.bot.delete_message(
                    chat_id=chat_id,
                    message_id=update.message.message_id)
                updater.bot.send_message(
                    chat_id=chat_id,
                    text=f'Welcome to BNBit, {update.message.from_user.first_name}!',
                )
        except Exception as e: print(e)

    def error(update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)

    # Listen for messages and moderate them.
    dp.add_handler(MessageHandler(Filters.text, moderate))

    # Send all errors to the logger.
    dp.add_error_handler(error)

    updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    updater.idle()


if __name__ == '__main__':
    main()
