"""Snips
Available Commands:
.snips
.snipl
.snipd"""

import io
import logging

from sample_config import Config
from userbot import bot
from userbot.database.snipsdb import add, check, check_one, delete_one
from userbot.util import admin_cmd

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(admin_cmd(pattern=r'\#(\S+)', outgoing=True))
async def on_snip(event):
    name = event.pattern_match.group(1)
    snip = await check_one(name)
    reply_message = await event.get_reply_message()
    if snip:
        await event.delete()
        msg_o = await event.client.get_messages(
            entity=Config.PRIVATE_CHANNEL_BOT_API_ID,
            ids=int(snip['Value'])
        )
        if msg_o.media is not None:
            if reply_message:
                await event.client.send_file(
                    event.chat_id,
                    msg_o.media,
                    supports_streaming=True,
                    reply_to=reply_message.id
                )
            else:
                await event.client.send_file(
                    event.chat_id,
                    msg_o.media,
                    supports_streaming=True
                )
        else:
            if reply_message:
                await event.client.send_message(
                    entity=event.chat_id,
                    message=msg_o.message,
                    reply_to=reply_message.id
                )
            else:
                await event.client.send_message(
                    entity=event.chat_id,
                    message=msg_o.message
                )


@bot.on(admin_cmd(pattern="snips (.*)"))
async def on_snip_save(event):
    name = event.pattern_match.group(1)
    msg = await event.get_reply_message()
    if msg:
        msg_o = await event.client.forward_messages(
            entity=Config.PRIVATE_CHANNEL_BOT_API_ID,
            messages=msg,
            from_peer=event.chat_id,
            silent=True
        )
        if not await check_one(name):
            await add(name, msg_o.id)
            await event.edit("snip {name} saved successfully. Get it with #{name}".format(name=name))
        else:
            await event.edit("snip {name} already have it. Get it with #{name}".format(name=name))
    else:
        await event.edit("Reply to a message with `snips keyword` to save the snip")


@bot.on(admin_cmd(pattern="snipl"))
async def on_snip_list(event):
    all_snips = await check()
    OUT_STR = "Available Snips:\n"
    if all_snips:
        for a_snip in all_snips:
            OUT_STR += f"👉 #{a_snip['Key']} \n"
    else:
        OUT_STR = "No Snips. Start Saving using `.snips`"
    if len(OUT_STR) > Config.MAX_MESSAGE_SIZE_LIMIT:
        with io.BytesIO(str.encode(OUT_STR)) as out_file:
            out_file.name = "snips.text"
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                caption="Available Snips",
                reply_to=event
            )
            await event.delete()
    else:
        await event.edit(OUT_STR)


@bot.on(admin_cmd(pattern="snipd (\S+)"))
async def on_snip_delete(event):
    name = event.pattern_match.group(1)
    await delete_one(name)
    await event.edit("snip #{} deleted successfully".format(name))
