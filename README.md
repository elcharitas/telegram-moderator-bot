Example Bot to moderate to Telegram group messages.

Run as:

```
MODERATOR_BOT_TOKEN=MYTOKEN python moderator.py
```

First, get the auth token for the bot, [talk to @BotFather](https://core.telegram.org/bots#6-botfather) to do that.

Now add the bot to the group and make it admin.
How to add bot to group: https://stackoverflow.com/questions/37338101

To get all messages in the group, also set the bot privacy mode to 'Disabled' (via @BotFather), the `/setprivacy` command.
See: https://stackoverflow.com/questions/38565952

Bot also needs to be admin, check the group settings (pencil icon at the top).

Other references:

- http://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.html
- https://core.telegram.org/bots/api#available-methods
