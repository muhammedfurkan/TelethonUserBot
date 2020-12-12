import asyncio
import logging

from sample_config import Config
from userbot import bot
from userbot.util import admin_cmd

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(admin_cmd(pattern=("mailru ?(.*)")))
async def _(event):
    url = event.pattern_match.group(1)
    if event.fwd_from:
        return
    event.pattern_match.group(1)
    await event.edit("Processing ...")
    await event.get_reply_message()
    try:
        downloaded_file_name = Config.TMP_DOWNLOAD_DIRECTORY
        await event.edit("Finish downloading to my local")
        command_to_exec = [
            "./userbot/bin/cmrudl.py",
            url,
            "-d",
            downloaded_file_name
        ]
        process = await asyncio.create_subprocess_shell(
            command_to_exec, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout.decode():
            std = stdout.decode()
            stds = std.split("\n")
            std1 = stds[1]
            std2 = stds[2]
            std3 = stds[3]
            out = str(std1)+"\n"+str(std2)+"\n"+str(std3)
            await event.edit(f"**{out}**")
        if stderr.decode():
            await event.edit(f"**{stderr.decode()}**")
            return
    except Exception as e:
        print(e)
