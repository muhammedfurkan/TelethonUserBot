# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import asyncio
import logging

from telethon import events

from userbot import bot

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


_last_messages = {}


@bot.on(events.NewMessage(outgoing=True))
async def _(event):
    _last_messages[event.chat_id] = event.message


@bot.on(events.NewMessage(pattern=r"\.(fix)?reply", outgoing=True))
async def _(event):
    if not event.is_reply or event.chat_id not in _last_messages:
        return

    message = _last_messages[event.chat_id]
    chat = await event.get_input_chat()
    await asyncio.wait([
        bot.delete_messages(chat, [event.id, message.id]),
        bot.send_message(chat, message, reply_to=event.reply_to_msg_id)
    ])
