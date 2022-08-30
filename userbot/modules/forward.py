import asyncio
import logging

from telethon import events
from telethon.errors import FloodWaitError
from userbot import bot

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s", level=logging.WARNING
)
logger = logging.getLogger(__name__)


@bot.on(events.NewMessage(func=lambda e: e.document, incoming=True))
async def _(event):
    media_mime = [
        "application/zip",
        "application/x-rar-compressed",
        "application/x-rar",
        "application/x-7z-compressed",
        "application/pdf",
    ]
    try:
        if event.media.document.mime_type in media_mime:
            await event.client.send_message(
                entity="DosyaAraBot",
                message="**DosyaAraBot**\n\n",
                file=event.media,
            )
    except AttributeError:
        return
    except FloodWaitError as e:
        await asyncio.sleep(e.seconds)
