""" command: .unzip
coded by @By_Azade
code rewritten my SnapDragon7410
"""
import asyncio
import logging
import os
import shutil
import time
import zipfile
from datetime import datetime
from glob import glob

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from sample_config import Config
from telethon.tl.types import DocumentAttributeVideo
from userbot import bot
from userbot.util import admin_cmd, progress

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)

# HACK :)-----------------------------------------------


def open_zip(zip_yolu: str):
    with open(zip_yolu, 'rb') as zip_dosyasi:
        z = zipfile.ZipFile(zip_dosyasi, allowZip64=True)
        for eleman in z.infolist():
            try:
                return z.extract(eleman)
            except zipfile.error as hata:
                return hata

# HACK :)------------------------------------------------


def opened_zip(zip_yolu: str):
    for adres in os.walk(zip_yolu.split('.zip')[0]):
        # 2. İndex Dosyalara Denk Geliyor!
        if adres[2]:
            for dosya in adres[2]:
                return f"{adres[0]}/{dosya}"


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
                    duration = metadata.get('duration').seconds if metadata.has("duration") else 0
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
