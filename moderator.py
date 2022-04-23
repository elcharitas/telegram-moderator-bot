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

from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import (
    Updater,
    CommandHandler,MessageHandler,
    CallbackQueryHandler,
    Filters,
    CallbackContext,
)

# Enable logging
from telegram.utils import helpers
from profanity import profanity
# from deep_translator import GoogleTranslator
import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define constants that will allow us to reuse the deep-linking parameters.
CHECK_THIS_OUT = "check-this-out"
USING_ENTITIES = "using-entities-here"
USING_KEYBOARD = "using-keyboard-here"
SO_COOL = "so-cool"

# Callback data to pass in 3rd level deep-linking


DISALLOWED_WORDS = {
    'scam',
    'signup here',
    'join my group',
    'register and get',
    'Sign up',
    'Scam',
    'Fuck',
    'Shit'
}
def start(update: Update, context: CallbackContext) -> None:
    """Send a deep-linked URL when the command /start is issued."""
    bot = context.bot
    url = helpers.create_deep_linked_url(bot.username, CHECK_THIS_OUT, group=True)
    text = "Feel free to tell your friends about it:\n\n" + url
    update.message.reply_text(text)


def deep_linked_level_1(update: Update, context: CallbackContext) -> None:
    """Reached through the CHECK_THIS_OUT payload"""
    bot = context.bot
    url = helpers.create_deep_linked_url(bot.username, SO_COOL)
    text = (
        "Awesome, you just accessed hidden functionality! "
        "Now let's get back to the private chat."
    )
    keyboard = InlineKeyboardMarkup.from_button(
        InlineKeyboardButton(text="Continue here!", url=url)
    )
    update.message.reply_text(text, reply_markup=keyboard)


def deep_linked_level_2(update: Update, context: CallbackContext) -> None:
    """Reached through the SO_COOL payload"""
    bot = context.bot
    url = helpers.create_deep_linked_url(bot.username, USING_ENTITIES)
    text = f"You can also mask the deep-linked URLs as links: [▶️ CLICK HERE]({url})."
    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


def deep_linked_level_3(update: Update, context: CallbackContext) -> None:
    """Reached through the USING_ENTITIES payload"""
    update.message.reply_text(
        "It is also possible to make deep-linking using InlineKeyboardButtons.",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Like this!", callback_data=KEYBOARD_CALLBACKDATA)]]
        ),
    )


def deep_link_level_3_callback(update: Update, context: CallbackContext) -> None:
    """Answers CallbackQuery with deeplinking url."""
    bot = context.bot
    url = helpers.create_deep_linked_url(bot.username, USING_KEYBOARD)
    update.callback_query.answer(url=url)


def deep_linked_level_4(update: Update, context: CallbackContext) -> None:
    """Reached through the USING_KEYBOARD payload"""
    payload = context.args
    update.message.reply_text(
        f"Congratulations! This is as deep as it gets 👏🏻\n\nThe payload was: {payload}"
    )


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
        # text = GoogleTranslator('auto','en').translate(text)
        words = set(text.lower().split())
        if words.intersection(DISALLOWED_WORDS):
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
                        text=f'@{update.message.from_user.username}, I had to delete your message as it contains censored words. Please refrain from using profain words.',
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
# Register a deep-linking handler
    dp.add_handler(
        CommandHandler("start", deep_linked_level_1, Filters.regex(CHECK_THIS_OUT))
    )

    # This one works with a textual link instead of an URL
    dp.add_handler(CommandHandler("start", deep_linked_level_2, Filters.regex(SO_COOL)))

    # We can also pass on the deep-linking payload
    dp.add_handler(
        CommandHandler("start", deep_linked_level_3, Filters.regex(USING_ENTITIES))
    )

    # Possible with inline keyboard buttons as well
    dp.add_handler(
        CommandHandler("start", deep_linked_level_4, Filters.regex(USING_KEYBOARD))
    )

    # register callback handler for inline keyboard button
    dp.add_handler(
        CallbackQueryHandler(deep_link_level_3_callback, pattern=KEYBOARD_CALLBACKDATA)
    )

    # Make sure the deep-linking handlers occur *before* the normal /start handler.
    dp.add_handler(CommandHandler("start", start))

    # Send all errors to the logger.
    dp.add_error_handler(error)

    updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    updater.idle()


if __name__ == '__main__':
    main()
