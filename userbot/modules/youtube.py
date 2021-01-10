#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the GNU
# General Public License, v.3.0. If a copy of the GPL was not distributed with this
# file, You can obtain one at https://www.gnu.org/licenses/gpl-3.0.en.html
from __future__ import unicode_literals

import json
import logging
import os
import time
from datetime import datetime

import youtube_dl
from telethon import events

from sample_config import Config
from userbot import bot

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(events.MessageEdited(pattern=r"\.youtube search (.*)", outgoing=True))  # pylint:disable=E0602
async def _(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    await event.edit("checking ...")
    start = datetime.now()
    c_time = time.time()
    download_file_name = Config.TMP_DOWNLOAD_DIRECTORY + "/youtubevideo.mp4"
    ydl_opts = {
        "format": "best",
        "progress_hooks": [
            lambda d: ytdl_progress(d, event, c_time)
        ],
        "quiet": True,
        "outtmpl": download_file_name
    }
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(["ytsearch:{}".format(input_str)])
    end = datetime.now()
    ms = (end - start).seconds
    await event.edit("Downloaded to `{}` in {} seconds.".format(download_file_name, ms))


async def ytdl_progress(d, event, start):
    now = time.time()
    diff = now - start
    status = d["status"]
    if round(diff % 10.00) == 0 or status == "finished":
        if status == "error":
            print(json.dumps(d))
        elif status == "downloading":
            speed = d["speed"]
            time_to_completion = d["eta"]
            filename = d["filename"]
            await event.edit("""File Name: {}
Speed: {}
ETA: {}""".format(filename, speed, time_to_completion))
