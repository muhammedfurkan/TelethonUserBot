# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import logging

from telethon import events
from telethon.tl.functions.messages import SaveDraftRequest

from userbot import bot

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(events.NewMessage(pattern=r"\.chain", outgoing=True))
async def _(event):
    await event.edit("Counting...")
    count = -1
    message = event.message
    while message:
        reply = await message.get_reply_message()
        if reply is None:
            await bot(SaveDraftRequest(
                await event.get_input_chat(),
                "",
                reply_to_msg_id=message.id
            ))
        message = reply
        count += 1
    await event.edit(f"Chain length: {count}")
