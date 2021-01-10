"""IX.IO pastebin like site
Syntax: .paste"""
import logging
import os
from datetime import datetime

import requests

from sample_config import Config
from userbot import bot
from userbot.util import admin_cmd

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


def progress(current, total):
    logger.info("Downloaded {} of {}\nCompleted {}".format(
        current, total, (current / total) * 100))


@bot.on(admin_cmd(pattern="paste ?(.*)"))
async def _(event):
    if event.fwd_from:
        return
    start = datetime.now()
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    input_str = event.pattern_match.group(1)
    message = "SYNTAX: `.paste <long text to include>`"
    if input_str:
        message = input_str
    elif event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        if previous_message.media:
            downloaded_file_name = await previous_message.download_media(
                Config.TMP_DOWNLOAD_DIRECTORY,
                progress_callback=progress
            )
            m_list = None
            with open(downloaded_file_name, "rb") as fd:
                m_list = fd.readlines()
            message = ""
            for m in m_list:
                # message += m.decode("UTF-8") + "\r\n"
                message += m.decode("UTF-8")
            os.remove(downloaded_file_name)
        else:
            message = previous_message.message
    else:
        message = "SYNTAX: `.paste <long text to include>`"
    url = "https://del.dog/documents"
    r = requests.post(url, data=message.encode("UTF-8")).json()
    url = f"https://del.dog/{r['key']}"
    end = datetime.now()
    ms = (end - start).seconds
    if r["isUrl"]:
        nurl = f"https://del.dog/v/{r['key']}"
        await event.edit("Dogged to {} in {} seconds. GoTo Original URL: {}".format(url, ms, nurl))
    else:
        await event.edit("Dogged to {} in {} seconds".format(url, ms))
