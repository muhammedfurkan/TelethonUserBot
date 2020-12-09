"""Profile Updation Commands
.pbio <Bio>
.pname <Name>
.ppic"""
import datetime
import logging
import os
from datetime import datetime

from telethon.tl import functions

from sample_config import Config
from userbot import bot
from userbot.util import admin_cmd, register

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(admin_cmd(pattern="pbio (.*)"))  # pylint:disable=E0602
async def _(event):
    if event.fwd_from:
        return
    bio = event.pattern_match.group(1)
    try:
        await bot(functions.account.UpdateProfileRequest(
            about=bio
        ))
        await event.edit("Succesfully changed my profile bio")
    except Exception as e:  # pylint:disable=C0103,W0703
        await event.edit(str(e))


@bot.on(admin_cmd(pattern="pname ((.|\n)*)"))  # pylint:disable=E0602,W0703
async def _(event):
    if event.fwd_from:
        return
    names = event.pattern_match.group(1)
    first_name = names
    last_name = ""
    if "\\n" in names:
        first_name, last_name = names.split("\\n", 1)
    try:
        await bot(functions.account.UpdateProfileRequest(
            first_name=first_name,
            last_name=last_name
        ))
        await event.edit("My name was changed successfully")
    except Exception as e:  # pylint:disable=C0103,W0703
        await event.edit(str(e))


@bot.on(admin_cmd(pattern="ppic"))  # pylint:disable=E0602
async def _(event):
    if event.fwd_from:
        return
    reply_message = await event.get_reply_message()
    await event.edit("Downloading Profile Picture to my local ...")
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    photo = None
    try:
        photo = await bot.download_media(
            reply_message,
            Config.TMP_DOWNLOAD_DIRECTORY
        )
    except Exception as e:  # pylint:disable=C0103,W0703
        await event.edit(str(e))
    else:
        if photo:
            await event.edit("now, Uploading to @Telegram ...")
            file = await bot.upload_file(photo)
            try:
                await bot(functions.photos.UploadProfilePhotoRequest(
                    file
                ))
            except Exception as e:  # pylint:disable=C0103,W0703
                await event.edit(str(e))
            else:
                await event.edit("My profile picture was succesfully changed")
    try:
        os.remove(photo)
    except Exception as e:  # pylint:disable=C0103,W0703
        logger.warning(str(e))


@bot.on(admin_cmd(pattern="pf (.*)"))
async def _(event):
    """getting user profile photo last changed time"""
    if event.fwd_from:
        return
    p_number = event.pattern_match.group(1)
    reply_message = await event.get_reply_message()
    if event.is_group:
        entity = await event.client.get_entity(reply_message.sender_id)
        try:
            a = await event.edit("`getting profile pic changed or added date`")
            photos = await event.client.get_profile_photos(entity)
            if photos.total == 0:
                await event.edit("`This user has no profile photos.`")
            else:
                msg = photos[int(p_number)].date
                print(msg)
                d = datetime.datetime.strptime(str(msg), "%Y-%m-%d %H:%M:%S%z")
                d = d.replace(tzinfo=datetime.timezone.utc)
                d = d.astimezone()
                msg_utc = d.strftime("%d %m %Y %H:%M:%S")
                msg = "Last profile photo changed: \n👉 `{}` `UTC+3`".format(
                    str(msg_utc))
                await a.edit(msg)
        except:
            pass

    else:
        entity = await event.client.get_entity(event.chat_id)
        try:
            a = await event.edit("`getting profile pic changed or added date`")
            photos = await bot.get_profile_photos(entity)
            if photos.total == 0:
                await event.edit("`This user has no profile photos.`")
            else:
                msg = photos[int(p_number)].date
                d = datetime.datetime.strptime(str(msg), "%Y-%m-%d %H:%M:%S%z")
                d = d.replace(tzinfo=datetime.timezone.utc)
                d = d.astimezone()
                msg_utc = d.strftime("%d %m %Y %H:%M:%S")
                msg = "Last profile photo changed: \n👉 `{}` `UTC+3`".format(
                    str(msg_utc))
                await a.edit(msg)
        except:
            pass
