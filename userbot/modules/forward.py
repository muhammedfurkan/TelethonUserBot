import logging

from telethon import events

from userbot import bot

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(events.NewMessage(func=lambda e: e.document))
async def _(event):
    media_mime = ["application/zip", "application/x-rar-compressed",
                  "application/x-rar", "application/x-7z-compressed", "application/pdf"]
    try:
        await event.client.send_message(
            entity="DosyaAraBot",
            message="**DosyaAraBot**\n\n",
            file=event.media if event.message.media.document.mime_type in media_mime else event.media,
        )
    except AttributeError:
        return
