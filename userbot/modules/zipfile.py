import asyncio
import logging
import os
import shutil
import time
import zipfile
from datetime import datetime
from glob import glob

import patoolib
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from sample_config import Config
from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeVideo
from userbot import bot
from userbot.util import admin_cmd, progress

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(admin_cmd(pattern=("zip ?(.*)")))
async def _(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    mone = await event.edit("Processing ...")
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    if event.reply_to_msg_id:
        reply_message = await event.get_reply_message()
        try:
            c_time = time.time()
            downloaded_file_name = await bot.download_media(
                reply_message,
                Config.TMP_DOWNLOAD_DIRECTORY,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, mone, c_time, "trying to download")
                )
            )
            directory_name = downloaded_file_name
            await event.edit("Finish downloading to my local")
            zipfile.ZipFile(directory_name + '.zip', 'w',
                            zipfile.ZIP_DEFLATED).write(directory_name)
            await bot.send_file(
                event.chat_id,
                directory_name + ".zip",
                caption="Zipped By @By_Azade",
                force_document=True,
                allow_cache=False,
                reply_to=event.message.id,
            )
            try:
                os.remove(directory_name + ".zip")
                os.remove(directory_name)
            except:
                pass
            await event.edit("Task Completed")
            await asyncio.sleep(3)
            await event.delete()
        except Exception as e:  # pylint:disable=C0103,W0703
            await mone.edit(str(e))
    elif input_str:
        directory_name = input_str
        zipfile.ZipFile(directory_name + '.zip', 'w',
                        zipfile.ZIP_DEFLATED).write(directory_name)
        await event.edit("Local file compressed to `{}`".format(directory_name + ".zip"))


@bot.on(admin_cmd(pattern="unzip"))
async def _(event):
    if event.fwd_from:
        return
    mone = await event.edit("Processing ...")
    extracted = Config.TMP_DOWNLOAD_DIRECTORY + "extracted/"
    thumb_image_path = Config.TMP_DOWNLOAD_DIRECTORY + "/thumb_image.jpg"
    if not os.path.isdir(extracted):
        os.makedirs(extracted)
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    if event.reply_to_msg_id:
        start = datetime.now()
        reply_message = await event.get_reply_message()
        try:
            c_time = time.time()
            downloaded_file_name = await bot.download_media(
                reply_message,
                Config.TMP_DOWNLOAD_DIRECTORY,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, mone, c_time, "trying to download")
                )
            )
        except Exception as e:  # pylint:disable=C0103,W0703
            await mone.edit(str(e))
        else:
            end = datetime.now()
            ms = (end - start).seconds
            await mone.edit("Stored the zip to `{}` in {} seconds.".format(downloaded_file_name, ms))

        shutil.unpack_archive(downloaded_file_name, extracted)
        files = [f for f in glob("./DOWNLOADS/extracted/**",
                                 recursive=True) if os.path.isfile(f)]
        filename = set(list(files))
        # NOTE no need this
        # with zipfile.ZipFile(downloaded_file_name, 'r') as zip_ref:
        #     zip_ref.extractall(extracted)
        # filename = sorted(get_lst_of_files(extracted, []))
        #filename = filename + "/"
        await event.edit("Unzipping now")
        # r=root, d=directories, f = files
        for single_file in filename:
            if os.path.exists(single_file):
                # https://stackoverflow.com/a/678242/4723940
                caption_rts = os.path.basename(single_file)
                force_document = False
                supports_streaming = True
                document_attributes = []
                if single_file.endswith((".mp4", ".mp3", ".flac", ".webm")):
                    metadata = extractMetadata(createParser(single_file))
                    width = 0
                    height = 0
                    duration = metadata.get(
                        'duration').seconds if metadata.has("duration") else 0
                    if os.path.exists(thumb_image_path):
                        metadata = extractMetadata(
                            createParser(thumb_image_path))
                        if metadata.has("width"):
                            width = metadata.get("width")
                        if metadata.has("height"):
                            height = metadata.get("height")
                    document_attributes = [
                        DocumentAttributeVideo(
                            duration=duration,
                            w=width,
                            h=height,
                            round_message=False,
                            supports_streaming=True
                        )
                    ]
                try:
                    await bot.send_file(
                        event.chat_id,
                        single_file,
                        caption=f"`{caption_rts}`",
                        force_document=force_document,
                        supports_streaming=supports_streaming,
                        allow_cache=False,
                        reply_to=event.message.id,
                        attributes=document_attributes,
                        # progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                        #     progress(d, t, event, c_time, "trying to upload")
                        # )
                    )
                except Exception as e:
                    await bot.send_message(
                        event.chat_id,
                        "{} caused `{}`".format(caption_rts, str(e)),
                        reply_to=event.message.id
                    )
                    # some media were having some issues
                    continue
                os.remove(single_file)
        os.remove(downloaded_file_name)
        await event.reply("`Unzip finished.`")
    await asyncio.sleep(2)
    shutil.rmtree(Config.TMP_DOWNLOAD_DIRECTORY)


@bot.on(admin_cmd(pattern="untar"))
async def _(event):
    if event.fwd_from:
        return
    mone = await event.edit("Processing ...")
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    extracted = Config.TMP_DOWNLOAD_DIRECTORY + "extracted/"
    thumb_image_path = Config.TMP_DOWNLOAD_DIRECTORY + "/thumb_image.jpg"
    if not os.path.isdir(extracted):
        os.makedirs(extracted)
    if event.reply_to_msg_id:
        start = datetime.now()
        reply_message = await event.get_reply_message()
        try:
            c_time = time.time()
            downloaded_file_name = await bot.download_media(
                reply_message,
                Config.TMP_DOWNLOAD_DIRECTORY,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, mone, c_time, "trying to download")
                )
            )
        except Exception as e:  # pylint:disable=C0103,W0703
            await mone.edit(str(e))
        else:
            end = datetime.now()
            ms = (end - start).seconds
            await mone.edit("Stored the tar to `{}` in {} seconds.".format(downloaded_file_name, ms))

        shutil.unpack_archive(downloaded_file_name, extracted)
        files = [f for f in glob("./DOWNLOADS/extracted/**",
                                 recursive=True) if os.path.isfile(f)]
        filename = set(list(files))
        # with tarfile.TarFile.open(downloaded_file_name, 'r') as tar_file:
        #     tar_file.extractall(path=extracted)
        # tf = tarfile.open(downloaded_file_name)
        # tf.extractall(path=extracted)
        # tf.close()

        # with zipfile.ZipFile(downloaded_file_name, 'r') as zip_ref:
        #     zip_ref.extractall(extracted)
        # filename = sorted(get_lst_of_files(extracted, []))
        #filename = filename + "/"
        await event.edit("Untarring now")
        # r=root, d=directories, f = files
        for single_file in filename:
            if os.path.exists(single_file):
                # https://stackoverflow.com/a/678242/4723940
                caption_rts = os.path.basename(single_file)
                force_document = False
                supports_streaming = True
                document_attributes = []
                if single_file.endswith((".mp4", ".mp3", ".flac", ".webm")):
                    metadata = extractMetadata(createParser(single_file))
                    width = 0
                    height = 0
                    duration = metadata.get(
                        'duration').seconds if metadata.has("duration") else 0
                    if os.path.exists(thumb_image_path):
                        metadata = extractMetadata(
                            createParser(thumb_image_path))
                        if metadata.has("width"):
                            width = metadata.get("width")
                        if metadata.has("height"):
                            height = metadata.get("height")
                    document_attributes = [
                        DocumentAttributeVideo(
                            duration=duration,
                            w=width,
                            h=height,
                            round_message=False,
                            supports_streaming=True
                        )
                    ]
                try:
                    await bot.send_file(
                        event.chat_id,
                        single_file,
                        caption=f"UnZipped `{caption_rts}`",
                        force_document=force_document,
                        supports_streaming=supports_streaming,
                        allow_cache=False,
                        reply_to=event.message.id,
                        attributes=document_attributes,
                        # progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                        #     progress(d, t, event, c_time, "trying to upload")
                        # )
                    )
                except Exception as e:
                    await bot.send_message(
                        event.chat_id,
                        "{} caused `{}`".format(caption_rts, str(e)),
                        reply_to=event.message.id
                    )
                    # some media were having some issues
                    continue
                os.remove(single_file)
        os.remove(downloaded_file_name)
        await event.reply("`Untar finished.`")
    await asyncio.sleep(2)
    shutil.rmtree(Config.TMP_DOWNLOAD_DIRECTORY)


@bot.on(admin_cmd(pattern="unrar"))
async def _(event):
    if event.fwd_from:
        return
    mone = await event.edit("Processing ...")
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    extracted = Config.TMP_DOWNLOAD_DIRECTORY + "extracted/"
    thumb_image_path = Config.TMP_DOWNLOAD_DIRECTORY + "/thumb_image.jpg"
    if not os.path.isdir(extracted):
        os.makedirs(extracted)
    if event.reply_to_msg_id:
        start = datetime.now()
        reply_message = await event.get_reply_message()
        try:
            c_time = time.time()
            downloaded_file_name = await bot.download_media(
                reply_message,
                Config.TMP_DOWNLOAD_DIRECTORY,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, mone, c_time, "trying to download")
                )
            )
        except Exception as e:  # pylint:disable=C0103,W0703
            await mone.edit(str(e))
        else:
            end = datetime.now()
            ms = (end - start).seconds
            await mone.edit("Stored the rar to `{}` in {} seconds.".format(downloaded_file_name, ms))

        patoolib.extract_archive(downloaded_file_name, outdir=extracted)
        files = [f for f in glob("./DOWNLOADS/extracted/**",
                                 recursive=True) if os.path.isfile(f)]
        filename = set(list(files))
        # filename = sorted(get_lst_of_files(extracted, []))
        #filename = filename + "/"
        await event.edit("Unraring now")
        # r=root, d=directories, f = files
        for single_file in filename:
            if os.path.exists(single_file):
                # https://stackoverflow.com/a/678242/4723940
                caption_rts = os.path.basename(single_file)
                force_document = False
                supports_streaming = True
                document_attributes = []
                if single_file.endswith((".mp4", ".mp3", ".flac", ".webm")):
                    metadata = extractMetadata(createParser(single_file))
                    width = 0
                    height = 0
                    duration = metadata.get(
                        'duration').seconds if metadata.has("duration") else 0
                    if os.path.exists(thumb_image_path):
                        metadata = extractMetadata(
                            createParser(thumb_image_path))
                        if metadata.has("width"):
                            width = metadata.get("width")
                        if metadata.has("height"):
                            height = metadata.get("height")
                    document_attributes = [
                        DocumentAttributeAudio(
                            duration=duration,
                            w=width,
                            h=height,
                            round_message=False,
                            supports_streaming=True
                        )
                    ]
                try:
                    await bot.send_file(
                        event.chat_id,
                        single_file,
                        caption=f"UnRarred `{caption_rts}`",
                        force_document=force_document,
                        supports_streaming=supports_streaming,
                        allow_cache=False,
                        reply_to=event.message.id,
                        attributes=document_attributes,
                        # progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                        #     progress(d, t, event, c_time, "trying to upload")
                        # )
                    )
                except Exception as e:
                    await bot.send_message(
                        event.chat_id,
                        "{} caused `{}`".format(caption_rts, str(e)),
                        reply_to=event.message.id
                    )
                    # some media were having some issues
                    continue
                os.remove(single_file)
        os.remove(downloaded_file_name)
        await event.reply("`Unrar finished.`")
    await asyncio.sleep(2)
    shutil.rmtree(Config.TMP_DOWNLOAD_DIRECTORY)


def get_lst_of_files(input_directory, output_lst):
    filesinfolder = os.listdir(input_directory)
    for file_name in filesinfolder:
        current_file_name = os.path.join(input_directory, file_name)
        if os.path.isdir(current_file_name):
            return get_lst_of_files(current_file_name, output_lst)
        output_lst.append(current_file_name)
    return output_lst
