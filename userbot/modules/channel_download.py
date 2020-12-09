"""
Telegram Channel Media Downloader Plugin for userbot.
usage: .geta channel_username [will  get all media from channel, tho there is limit of 3000 there to prevent API limits.]
       .getc number_of_messsages channel_username  
By: @Zero_cool7870
"""
import asyncio
import logging
import os
import subprocess

from telethon import errors, events

from userbot import bot
from userbot.util import admin_cmd, register

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)

directory = "./temp/"


@bot.on(events.NewMessage(pattern=r"\.getc", outgoing=True))
async def get_media(event):
    if event.fwd_from:
        return
    dir = "./temp/"
    try:
        os.makedirs("./temp/")
    except:
        pass
    channel_username = event.text
    command = ['ls', 'temp', '|', 'wc', '-l']
    limit = channel_username[6:9]
    print(limit)
    channel_username = channel_username[11:]
    print(channel_username)
    await event.edit("Downloading Media From this Channel.")
    msgs = await bot.get_messages(channel_username, limit=int(limit))
    with open('log.txt', 'w') as f:
        f.write(str(msgs))
    for msg in msgs:
        if msg.media is not None:
            await bot.download_media(
                msg, dir)
    ps = subprocess.Popen(('ls', 'temp'), stdout=subprocess.PIPE)
    output = subprocess.check_output(('wc', '-l'), stdin=ps.stdout)
    ps.wait()
    output = str(output)
    output = output.replace("b'", "")
    output = output.replace("\n'", "")
    await event.edit("Downloaded "+output+" files.")


@bot.on(admin_cmd(pattern="geta ?(.*)", allow_sudo=True))
async def get_media(event):
    if event.fwd_from:
        return
    count = 0
    os.makedirs(directory, exist_ok=True)
    channel = event.pattern_match.group(1)
    try:
        channel = int(channel)
    except ValueError:
        pass
    await event.edit("Downloading All Media From this Channel.")
    msgs = await bot.get_messages(channel, limit=3000)
    for msg in msgs:
        if msg.media is not None:
            try:
                await bot.download_media(msg, directory)
                count += 1
            except errors.FloodWaitError as e:
                await asyncio.sleep(e.seconds)
    await event.edit(f"Downloaded {count} files.")
