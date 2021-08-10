# For @Unibot
# (c) Shrimadhav U K
import logging

from telethon import events, functions

from userbot import bot

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(events.NewMessage(pattern=r"\-listmyusernames", outgoing=True))
async def _(event):
    if event.fwd_from:
        return
    result = await bot(functions.channels.GetAdminedPublicChannelsRequest())
    output_str = "".join(
        f"- {channel_obj.title} @{channel_obj.username} \n"
        for channel_obj in result.chats
    )

    await event.edit(output_str)
