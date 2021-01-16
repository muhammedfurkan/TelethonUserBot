"""
Reply to a file with .f to send it as a photo
"""
import logging
from io import BytesIO

from telethon import types
from telethon.errors import PhotoInvalidDimensionsError
from telethon.tl.functions.messages import SendMediaRequest

from userbot import bot
from userbot.util import admin_cmd

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(admin_cmd(pattern="fp ?(.*)"))
async def on_file_to_photo(event):
    await event.delete()
    target = await event.get_reply_message()
    try:
        image = target.media.document
    except AttributeError:
        return
    if not image.mime_type.startswith('image/'):
        return  # This isn't an image
    if image.mime_type == 'image/webp':
        return  # Telegram doesn't let you directly send stickers as photos
    if image.size > 10 * 1024 * 1024:
        return  # We'd get PhotoSaveFileInvalidError otherwise

    file = await bot.download_media(target, file=BytesIO())
    file.seek(0)
    img = await bot.upload_file(file)
    img.name = 'image.png'

    try:
        await bot(SendMediaRequest(
            peer=await event.get_input_chat(),
            media=types.InputMediaUploadedPhoto(img),
            message=target.message,
            entities=target.entities,
            reply_to_msg_id=target.id
        ))
    except PhotoInvalidDimensionsError:
        return
