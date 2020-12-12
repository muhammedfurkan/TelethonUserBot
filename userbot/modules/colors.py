"""Color Plugin for @Unibot
Syntax: .color <color_code>"""
import logging
import os

from PIL import Image, ImageColor

from userbot import bot
from userbot.util import admin_cmd

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(admin_cmd(pattern="color (.*)"))
async def _(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    message_id = event.message.id
    if event.reply_to_msg_id:
        message_id = event.reply_to_msg_id
    if input_str.startswith("#"):
        try:
            usercolor = ImageColor.getrgb(input_str)
        except Exception as e:
            await event.edit(str(e))
            return False
        else:
            im = Image.new(mode="RGB", size=(1280, 720), color=usercolor)
            im.save("Unibot.png", "PNG")
            input_str = input_str.replace("#", "#COLOR_")
            await bot.send_file(
                event.chat_id,
                "Unibot.png",
                force_document=False,
                caption=input_str,
                reply_to=message_id
            )
            os.remove("Unibot.png")
            await event.delete()
    else:
        await event.edit("Syntax: `.color <color_code>`")
