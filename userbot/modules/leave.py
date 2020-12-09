import time

from telethon.tl.functions.channels import LeaveChannelRequest

from userbot import bot
from userbot.util import admin_cmd, register


@bot.on(admin_cmd(pattern="leave", outgoing=True))
async def leave(e):
    if not e.text[0].isalpha() and e.text[0] not in ("/", "#", "@", "!"):
        await e.delete()
        time.sleep(3)
        if '-' in str(e.chat_id):
            await bot(LeaveChannelRequest(e.chat_id))
        else:
            await e.edit('`This is Not A Chat`')
