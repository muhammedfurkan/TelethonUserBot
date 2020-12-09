# (c) @Unibot
# Original written by @Unibot edit by @INF1N17Y

import asyncio
import logging
from collections import deque

from telethon import events

from userbot import bot
from userbot.util import admin_cmd, register

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(events.NewMessage(pattern=r"\.kalp", outgoing=True))
async def _(event):
    if event.fwd_from:
        return
    deq = deque(list("💙💛💓💔💘💕💜💚💝💞💟"))
    for _ in range(100):
        await asyncio.sleep(0.1)
        await event.edit("".join(deq))
        deq.rotate(1)


@bot.on(admin_cmd(pattern="bkalp", outgoing=True))
async def bkallp(event):
    a = "❤️ 🧡 💛 💚 💙 💜 🖤 🤍 🤎 💔 💘 💝".split(" ")
    d = await event.reply("...")
    for t in a:
        await d.edit(t)
        await asyncio.sleep(5)
