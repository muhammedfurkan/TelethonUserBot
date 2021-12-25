# Thanks to @AvinashReddy3108 for this plugin

"""
Audio and video downloader using Youtube-dl
.yta To Download in mp3 format
.ytv To Download in mp4 format
"""
import asyncio
import logging
import math
import os
import shutil
import time
from typing import Dict, List

import aiofiles
import aiohttp
import pafy
import requests
from pytube import YouTube
from sample_config import Config
from telethon.tl.types import (DocumentAttributeAudio,
                               InputMediaDocumentExternal)
from userbot import bot
from userbot.util import admin_cmd
from yt_dlp import YoutubeDL as YtDL

from youtube_dl import YoutubeDL
from youtube_dl.utils import (ContentTooShortError, DownloadError,
                              ExtractorError, GeoRestrictedError,
                              MaxDownloadsReached, PostProcessingError,
                              UnavailableVideoError, XAttrMetadataError)

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


DELETE_TIMEOUT = 3


def get_audio_direct_link(yt_url: str, audio_quality: str) -> str:
    if audio_quality.lower() == "low":
        with YoutubeDL({"format": "worstaudio"}) as yt_dls:
            info = yt_dls.extract_info(yt_url, download=False)
            return info["url"]
    elif audio_quality.lower() in ["medium", "high"]:
        with YoutubeDL({"format": "bestaudio"}) as yt_dls:
            info = yt_dls.extract_info(yt_url, download=False)
            return info["url"]


def get_video_direct_link(yt_url: str, video_quality: str):
    ydl = YtDL()
    ress = ydl.extract_info(yt_url, download=False)
    yt_res: List[Dict[str, str]] = []
    for res in ress["formats"]:
        if res["ext"] == "mp4":
            if (
                video_quality.lower() == "low"
                and res["format_note"] == "360p"
                and res["acodec"] != "none"
            ):
                rus = {"quality": res["format_note"], "direct_url": res["url"]}
                yt_res.append(rus.copy())
            if (
                video_quality.lower() == "medium"
                and res["format_note"] == "480p"
                and res["acodec"] != "none"
            ):
                rus = {"quality": res["format_note"], "direct_url": res["url"]}
                yt_res.append(rus.copy())
            if (
                video_quality.lower() == "high"
                and res["format_note"] == "720p"
                and res["acodec"] != "none"
            ):
                rus = {"quality": res["format_note"], "direct_url": res["url"]}
                yt_res.append(rus.copy())
            if not yt_res and (
                res["format_note"] == "720p"
                and res["acodec"] != "none"
            ):
                rus = {"quality": res["format_note"], "direct_url": res["url"]}
                yt_res.append(rus.copy())
    return yt_res[0]["direct_url"]


def get_yt_details(link: str):
    yt = YouTube(link)
    return yt.title


def download_yt_thumbnails(thumb_url, user_id):
    r = requests.get(thumb_url)
    with open(f"search/thumb{user_id}.jpg", "wb") as file:
        for chunk in r.iter_content(1024):
            file.write(chunk)
    return f"search/thumb{user_id}.jpg"


def format_count(number: int):
    num = float(f"{number:.3g}")
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return f"{str(num).rstrip('0').rstrip('.')}{['', 'K', 'M', 'B', 'T'][magnitude]}"


async def progress(current, total, event, start, type_of_ps, file_name=None):
    """Generic progress_callback for uploads and downloads."""
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion
        progress_str = "{0}{1} {2}%\n".format(
            ''.join("█" for i in range(math.floor(percentage / 10))),
            ''.join("░" for i in range(10 - math.floor(percentage / 10))),
            round(percentage, 2))
        tmp = progress_str + \
            "{0} of {1}\nETA: {2}".format(
                humanbytes(current),
                humanbytes(total),
                time_formatter(estimated_total_time)
            )
        if file_name:
            await event.edit("{}\nFile Name: `{}`\n{}".format(
                type_of_ps, file_name, tmp))
        else:
            await event.edit("{}\n{}".format(type_of_ps, tmp))


def humanbytes(size):
    """Input size in bytes,
    outputs in a human readable format"""
    # https://stackoverflow.com/a/49361727/4723940
    if not size:
        return ""
    # 2 ** 10 = 1024
    power = 2**10
    raised_to_pow = 0
    dict_power_n = {0: "", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        raised_to_pow += 1
    return str(round(size, 2)) + " " + dict_power_n[raised_to_pow] + "B"


def time_formatter(milliseconds: int) -> str:
    """Inputs time in milliseconds, to get beautified time,
    as string"""
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + " day(s), ") if days else "") + \
        ((str(hours) + " hour(s), ") if hours else "") + \
        ((str(minutes) + " minute(s), ") if minutes else "") + \
        ((str(seconds) + " second(s), ") if seconds else "") + \
        ((str(milliseconds) + " millisecond(s), ") if milliseconds else "")
    return tmp[:-2]


@bot.on(admin_cmd(pattern="yt(a|v) (.*)"))
async def download_video(v_url):
    """ For .ytdl command, download media from YouTube and many other sites. """
    url = v_url.pattern_match.group(2)
    type = v_url.pattern_match.group(1).lower()
    out_folder = Config.TMP_DOWNLOAD_DIRECTORY + "youtubedl/"

    if not os.path.isdir(out_folder):
        os.makedirs(out_folder)

    await v_url.edit("`Preparing to download...`")
    c_time = time.time()
    if type == "a":
        # song = get_audio_direct_link(url, 'high')
        title = get_yt_details(url)
        yt = YouTube(url)
        yt.streams.all()  # list of all available streams
        # gives the direct url link of first stream
        direct_link = yt.streams[0].url
        await v_url.client.send_file(
            v_url.chat_id,
            file=InputMediaDocumentExternal(direct_link),
            reply_to=v_url.id,
            caption=f"`{title}`",
            supports_streaming=True,
            progress_callback=lambda d, t: asyncio.get_event_loop(
            ).create_task(
                progress(d, t, v_url, c_time, "Uploading..",
                         f"{title}.mp3"))
        )
        await v_url.delete()

    elif type == "v":
        # video = get_video_direct_link(url, 'high')
        title = get_yt_details(url)
        yt = YouTube(url)
        yt.streams.all()  # list of all available streams
        # gives the direct url link of first stream
        direct_link = yt.streams[0].url
        await v_url.client.send_file(
            v_url.chat_id,
            file=InputMediaDocumentExternal(direct_link),
            reply_to=v_url.id,
            caption=f"`{title}`",
            supports_streaming=True,
            progress_callback=lambda d, t: asyncio.get_event_loop(
            ).create_task(
                progress(d, t, v_url, c_time, "Uploading..",
                         f"{title}.mp4"))
        )
        await v_url.delete()


def get_lst_of_files(input_directory, output_lst):
    filesinfolder = os.listdir(input_directory)
    for file_name in filesinfolder:
        current_file_name = os.path.join(input_directory, file_name)
        if os.path.isdir(current_file_name):
            return get_lst_of_files(current_file_name, output_lst)
        output_lst.append(current_file_name)
    return output_lst


def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)
