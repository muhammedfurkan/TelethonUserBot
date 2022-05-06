import logging

from userbot import bot
from userbot.util import admin_cmd

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(admin_cmd(func=lambda e: e.media))
async def _(event):
    media_mime = ["application/zip", "application/x-rar-compressed", "application/x-rar", "application/x-7z-compressed","application/pdf"]
    try:
        e = await event.client.get_entity("DosyaAraBot")
    except Exception as e:
        await event.client.send_message("me", str(e))
    else:
        try:
            await event.client.send_message(
                entity="DosyaAraBot",
                message="**DosyaAraBot**\n\n",
                file=event.media if event.message.media.document.mime_type in media_mime else event.media,
            )
        except AttributeError as e:
            return

