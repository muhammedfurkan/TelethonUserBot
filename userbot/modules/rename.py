"""Rename Telegram Files
Syntax:
.rnupload file.name
.rnstreamupload file.name
By @Ck_ATR"""
import asyncio
import logging
import math
import os
import time
from datetime import datetime

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pySmartDL import SmartDL
from telethon.tl.types import DocumentAttributeVideo

from sample_config import Config
from userbot import bot
from userbot.util import admin_cmd, humanbytes, progress

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


thumb_image_path = Config.TMP_DOWNLOAD_DIRECTORY + "/thumb_image.jpg"


@bot.on(admin_cmd(pattern="rndlup (.*)"))
async def _(event):
    if event.fwd_from:
        return
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    thumb = thumb_image_path if os.path.exists(thumb_image_path) else None
    start = datetime.now()
    input_str = event.pattern_match.group(1)
    url = input_str
    file_name = os.path.basename(url)
    to_download_directory = Config.TMP_DOWNLOAD_DIRECTORY
    if "|" in input_str:
        url, file_name = input_str.split("|")
    url = url.strip()
    file_name = file_name.strip()
    downloaded_file_name = os.path.join(to_download_directory, file_name)
    downloader = SmartDL(url, downloaded_file_name, progress_bar=False)
    downloader.start(blocking=False)
    display_message = ""
    c_time = time.time()
    while not downloader.isFinished():
        total_length = downloader.filesize or None
        downloaded = downloader.get_dl_size()
        now = time.time()
        diff = now - c_time
        percentage = downloader.get_progress() * 100
        speed = downloader.get_speed()
        elapsed_time = round(diff) * 1000
        progress_str = "[{0}{1}]\nProgress: {2}%".format(
            ''.join("█" for i in range(math.floor(percentage / 5))),
            ''.join("░" for i in range(20 - math.floor(percentage / 5))),
            round(percentage, 2))
        estimated_total_time = downloader.get_eta(human=True)
        try:
            current_message = "trying to download\n"
            current_message += f"URL: {url}\n"
            current_message += f"File Name: {file_name}\n"
            current_message += f"{progress_str}\n"
            current_message += f"{humanbytes(downloaded)} of {humanbytes(total_length)}\n"
            current_message += f"ETA: {estimated_total_time}"
            if round(diff % 10.00) == 0 and current_message != display_message:
                await event.edit(current_message)
                display_message = current_message
        except Exception as e:
            logger.info(str(e))
    end = datetime.now()
    ms_dl = (end - start).seconds
    if downloader.isSuccessful():
        await event.edit("Downloaded to `{}` in {} seconds.".format(downloaded_file_name, ms_dl))
        if os.path.exists(downloaded_file_name):
            c_time = time.time()
            await event.client.send_file(
                event.chat_id,
                downloaded_file_name,
                force_document=True,
                supports_streaming=False,
                allow_cache=False,
                reply_to=event.message.id,
                thumb=thumb,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, event, c_time, "trying to upload")
                )
            )
            end_two = datetime.now()
            os.remove(downloaded_file_name)
            ms_two = (end_two - end).seconds
            a = await event.edit("Downloaded in {} seconds. Uploaded in {} seconds.".format(ms_dl, ms_two))
            await a.delete()
            await asyncio.sleep(5)
        else:
            await event.edit("File Not Found {}".format(input_str))
            await asyncio.sleep(5)
            await event.delete()
    else:
        await event.edit("Incorrect URL\n {}".format(input_str))


@bot.on(admin_cmd(pattern="rnupload (.*)"))
async def _(event):
    if event.fwd_from:
        return
    thumb = thumb_image_path if os.path.exists(thumb_image_path) else None
    await event.edit("Rename & Upload in process 🙄🙇‍♂️🙇‍♂️🙇‍♀️ It might take some time if file size is big")
    input_str = event.pattern_match.group(1)
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    if event.reply_to_msg_id:
        start = datetime.now()
        file_name = input_str
        reply_message = await event.get_reply_message()
        to_download_directory = Config.TMP_DOWNLOAD_DIRECTORY
        downloaded_file_name = os.path.join(to_download_directory, file_name)
        c_time = time.time()
        downloaded_file_name = await event.client.download_media(
            reply_message,
            downloaded_file_name,
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(d, t, event, c_time, "trying to download")
            )
        )
        end = datetime.now()
        ms_one = (end - start).seconds
        if os.path.exists(downloaded_file_name):
            c_time = time.time()
            await event.client.send_file(
                event.chat_id,
                downloaded_file_name,
                force_document=True,
                supports_streaming=False,
                allow_cache=False,
                reply_to=event.message.id,
                thumb=thumb,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, event, c_time, "trying to upload")
                )
            )
            end_two = datetime.now()
            os.remove(downloaded_file_name)
            ms_two = (end_two - end).seconds
            await event.edit("Downloaded in {} seconds. Uploaded in {} seconds.".format(ms_one, ms_two))
        else:
            await event.edit("File Not Found {}".format(input_str))
    else:
        await event.edit("Syntax // .rnupload file.name as reply to a Telegram media")


@bot.on(admin_cmd(pattern="rnstreamupload (.*)"))
async def _(event):
    if event.fwd_from:
        return
    await event.edit("Rename & Upload as Streamable in process 🙄🙇‍♂️🙇‍♂️🙇‍♀️ It might take some time if file size is big")
    input_str = event.pattern_match.group(1)
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    if event.reply_to_msg_id:
        start = datetime.now()
        file_name = input_str
        reply_message = await event.get_reply_message()
        c_time = time.time()
        to_download_directory = Config.TMP_DOWNLOAD_DIRECTORY
        downloaded_file_name = os.path.join(to_download_directory, file_name)
        downloaded_file_name = await event.client.download_media(
            reply_message,
            downloaded_file_name,
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(d, t, event, c_time, "trying to download")
            )
        )
        end_one = datetime.now()
        ms_one = (end_one - start).seconds
        if os.path.exists(downloaded_file_name):
            thumb = thumb_image_path if os.path.exists(thumb_image_path) else None
            start = datetime.now()
            metadata = extractMetadata(createParser(downloaded_file_name))
            width = 0
            height = 0
            duration = metadata.get('duration').seconds if metadata.has("duration") else 0
            if os.path.exists(thumb_image_path):
                metadata = extractMetadata(createParser(thumb_image_path))
                if metadata.has("width"):
                    width = metadata.get("width")
                if metadata.has("height"):
                    height = metadata.get("height")
            # Telegram only works with MP4 files
            # this is good, since with MKV files sent as streamable Telegram responds,
            # Bad Request: VIDEO_CONTENT_TYPE_INVALID
            c_time = time.time()
            try:
                await event.client.send_file(
                    event.chat_id,
                    downloaded_file_name,
                    thumb=thumb,
                    caption=downloaded_file_name,
                    force_document=False,
                    allow_cache=False,
                    reply_to=event.message.id,
                    attributes=[
                        DocumentAttributeVideo(
                            duration=duration,
                            w=width,
                            h=height,
                            round_message=False,
                            supports_streaming=True
                        )
                    ],
                    progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                        progress(d, t, event, c_time, "trying to upload")
                    )
                )
            except Exception as e:
                await event.edit(str(e))
            else:
                end = datetime.now()
                os.remove(downloaded_file_name)
                ms_two = (end - end_one).seconds
                await event.edit("Downloaded in {} seconds. Uploaded in {} seconds.".format(ms_one, ms_two))
        else:
            await event.edit("File Not Found {}".format(input_str))
    else:
        await event.edit("Syntax // .rnstreamupload file.name as reply to a Telegram media")
