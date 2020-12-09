"""Get ID of any Telegram media, or any user
Syntax: .get_id"""

import logging

from userbot import bot
from userbot.util import admin_cmd, register

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(admin_cmd(pattern="get_id"))
async def _(event):
    if event.fwd_from:
        return
    if event.reply_to_msg_id:
        chat = await event.get_input_chat()
        r_msg = await event.get_reply_message()
        if r_msg.media:
            await event.edit(
                "Current Chat ID: `{}`\nFrom User ID: `{}`\nBot API File ID: `{}`".format(
                    str(event.chat_id),
                    str(r_msg.sender_id),
                    r_msg.file.id
                )
            )
        else:
            await event.edit(
                "Current Chat ID: `{}`\nFrom User ID: `{}`".format(
                    str(event.chat_id),
                    str(r_msg.sender_id)
                )
            )
    else:
        await event.edit("Current Chat ID: `{}`".format(str(event.chat_id)))
