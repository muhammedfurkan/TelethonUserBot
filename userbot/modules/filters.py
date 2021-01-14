# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Filters
Available Commands:
.savef
.listf
.clearf
.clearaf"""
import asyncio
import io
import logging
import re

from sample_config import Config
from userbot import bot
from userbot.database.filtersdb import (add_filter, delete_all_filters,
                                        delete_filter, get_all_filters)
from userbot.util import admin_cmd

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)

DELETE_TIMEOUT = 300
last_triggered_filters = {}


@bot.on(admin_cmd(incoming=True))
async def on_snip(event):
    name = event.text
    if (
        event.chat_id in last_triggered_filters
        and name in last_triggered_filters[event.chat_id]
    ):
        # avoid userbot spam
        # "I demand rights for us bots, we are equal to you humans." -Henri Koivuneva (t.me/UserbotTesting/2698)
        return False
    snips = await get_all_filters(event.chat_id)
    if snips:
        for snip in snips:
            pattern = r"( |^|[^\w])" + \
                re.escape(snip['keyword']) + r"( |$|[^\w])"
            if re.fullmatch(pattern, name, flags=re.IGNORECASE):
                msg_o = await event.client.get_messages(
                    entity=Config.PRIVATE_CHANNEL_BOT_API_ID,
                    ids=int(snip['msg'])
                )
                message_id = event.message.id
                if event.reply_to_msg_id:
                    message_id = event.reply_to_msg_id
                await event.client.send_message(
                    event.chat_id,
                    msg_o.message,
                    reply_to=message_id,
                    file=msg_o.media
                )
                if event.chat_id not in last_triggered_filters:
                    last_triggered_filters[event.chat_id] = []
                last_triggered_filters[event.chat_id].append(name)
                await asyncio.sleep(DELETE_TIMEOUT)
                last_triggered_filters[event.chat_id].remove(name)


@bot.on(admin_cmd(pattern="savefilter (.*)"))
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
        await add_filter(event.chat_id, name, msg_o.id)
        await event.edit(f"Filter `{name}` saved successfully. Get it with `{name}`")
    else:
        await event.edit("Reply to a message with `savefilter keyword` to save the filter")


@ bot.on(admin_cmd(pattern="listfilters"))
async def on_snip_list(event):
    all_snips = await get_all_filters(event.chat_id)
    OUT_STR = "Available Filters in the Current Chat:\n"
    if all_snips:
        for a_snip in all_snips:
            OUT_STR += f"👉 {a_snip['keyword']} \n"
    else:
        OUT_STR = "No Filters. Start Saving using `.savefilter`"
    if len(OUT_STR) > Config.MAX_MESSAGE_SIZE_LIMIT:
        with io.BytesIO(str.encode(OUT_STR)) as out_file:
            out_file.name = "filters.text"
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                caption="Available Filters in the Current Chat",
                reply_to=event
            )
            await event.delete()
    else:
        await event.edit(OUT_STR)


@ bot.on(admin_cmd(pattern="clearfilter (.*)"))
async def on_snip_delete(event):
    name = event.pattern_match.group(1)
    await delete_filter(event.chat_id, name)
    await event.edit(f"Delete filter **{name}** deleted successfully")


@ bot.on(admin_cmd(pattern="clearallfilters"))
async def on_all_snip_delete(event):
    await delete_all_filters(event.chat_id)
    await event.edit("All filters **in current chat** deleted successfully")
