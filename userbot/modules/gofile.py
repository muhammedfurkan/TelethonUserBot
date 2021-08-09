"Plugin Created By https://t.me/By_Azade "


import logging
import shutil

from pygofile import Gofile
from userbot import Config, bot
from userbot.util import admin_cmd

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(admin_cmd(pattern="gofileup"))
async def go_file(event):
    await event.edit("`Downloading...`")
    API = Config.GO_FILE_API
    gofile = Gofile(token=API)

    if event.text is not None:
        reply = await event.get_reply_message()
        file_name = await event.client.download_media(
            reply.media,
            Config.TMP_DOWNLOAD_DIRECTORY
        )
        await event.edit("Downloaded, Now uploading file to GoFile.. Please wait..")

        data = await gofile.upload(file=file_name)

        print(data)
        await event.edit("**File Uploaded GoFile.**\n\n**Check your uploaded files here:** \n`{}`\n\n**Direct Link:** \n`{}`\n\n**Your file id:** \n`{}`\n\nIf you want to delete this file use `.gofiledel <fileID>` command.".format(data['downloadPage'], data['directLink'], data['fileId']))
        shutil.rmtree(Config.TMP_DOWNLOAD_DIRECTORY)


@bot.on(admin_cmd(pattern="gofiledel ?(.*)"))
async def go_file_del(event):
    await event.edit("`Progressing...`")
    API = Config.GO_FILE_API
    gofile = Gofile(token=API)
    match = event.pattern_match.group(1)
    if match:
        await gofile.delete_content(content_id=match)
        await event.edit("`File deleted..`")
