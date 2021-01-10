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

from telethon.tl.types import DocumentAttributeAudio
from youtube_dl import YoutubeDL
from youtube_dl.utils import (ContentTooShortError, DownloadError,
                              ExtractorError, GeoRestrictedError,
                              MaxDownloadsReached, PostProcessingError,
                              UnavailableVideoError, XAttrMetadataError)

from sample_config import Config
from userbot import bot
from userbot.util import admin_cmd

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


DELETE_TIMEOUT = 3


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

    if type == "a":
        opts = {
            'format': 'bestaudio',
            'addmetadata': True,
            'key': 'FFmpegMetadata',
            'writethumbnail': True,
            'embedthumbnail': True,
            'audioquality': 0,
            'audioformat': 'mp3',
            'prefer_ffmpeg': True,
            'geo_bypass': True,
            'nocheckcertificate': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'outtmpl': out_folder+'%(title)s.mp3',
            'quiet': True,
            'logtostderr': False
        }
        video = False
        song = True

    elif type == "v":
        opts = {
            'format': 'best',
            'addmetadata': True,
            'key': 'FFmpegMetadata',
            'writethumbnail': True,
            'write_all_thumbnails': True,
            'embedthumbnail': True,
            'prefer_ffmpeg': True,
            'hls_prefer_native': True,
            'geo_bypass': True,
            'nocheckcertificate': True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }],
            'outtmpl': out_folder+'%(title)s.mp4',
            'logtostderr': False,
            'quiet': True
        }
        song = False
        video = True

    try:
        await v_url.edit("`Fetching data, please wait..`")
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(url)
        filename = sorted(get_lst_of_files(out_folder, []))
    except DownloadError as DE:
        await v_url.edit(f"`{str(DE)}`")
        return
    except ContentTooShortError:
        await v_url.edit("`The download content was too short.`")
        return
    except GeoRestrictedError:
        await v_url.edit(
            "`Video is not available from your geographic location due to geographic restrictions imposed by a website.`"
        )
        return
    except MaxDownloadsReached:
        await v_url.edit("`Max-downloads limit has been reached.`")
        return
    except PostProcessingError:
        await v_url.edit("`There was an error during post processing.`")
        return
    except UnavailableVideoError:
        await v_url.edit("`Media is not available in the requested format.`")
        return
    except XAttrMetadataError as XAME:
        await v_url.edit(f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`")
        return
    except ExtractorError:
        await v_url.edit("`There was an error during info extraction.`")
        return
    except Exception as e:
        await v_url.edit(f"{str(type(e)): {str(e)}}")
        return
    c_time = time.time()

    # cover_url = f"https://img.youtube.com/vi/{ytdl_data['id']}/0.jpg"
    # thumb_path = wget.download(cover_url, out_folder + "cover.jpg")

    # relevant_path = "./DOWNLOADS/youtubedl"
    # included_extensions = ["mp4","mp3"]
    # file_names = [fn for fn in os.listdir(relevant_path)
    #             if any(fn.endswith(ext) for ext in included_extensions)]

    if song:
        relevant_path = "./DOWNLOADS/youtubedl"
        included_extensions = ["mp3"]
        file_names = [fn for fn in os.listdir(relevant_path)
                      if any(fn.endswith(ext) for ext in included_extensions)]
        img_extensions = ["webp", "jpg", "jpeg"]
        img_filenames = [fn_img for fn_img in os.listdir(relevant_path) if any(
            fn_img.endswith(ext_img) for ext_img in img_extensions)]
        thumb_image = out_folder + img_filenames[0]

        # thumb = out_folder + "cover.jpg"
        file_path = out_folder + file_names[0]
        song_size = file_size(file_path)
        j = await v_url.edit(f"`Preparing to upload song:`\
        \n**{ytdl_data['title']}**\
        \nby *{ytdl_data['uploader']}*")
        await v_url.client.send_file(
            v_url.chat_id,
            file_path,
            caption=ytdl_data['title'] + "\n" + f"`{song_size}`",
            supports_streaming=True,
            thumb=thumb_image,
            attributes=[
                DocumentAttributeAudio(duration=int(ytdl_data['duration']),
                                       title=str(ytdl_data['title']),
                                       performer=str(ytdl_data['uploader']))
            ],
            progress_callback=lambda d, t: asyncio.get_event_loop(
            ).create_task(
                progress(d, t, v_url, c_time, "Uploading..",
                         f"{ytdl_data['title']}.mp3")))
        # os.remove(file_path)
        await asyncio.sleep(DELETE_TIMEOUT)
        os.remove(thumb_image)
        await j.delete()

    elif video:
        relevant_path = "./DOWNLOADS/youtubedl/"
        included_extensions = ["mp4"]
        file_names = [fn for fn in os.listdir(relevant_path)
                      if any(fn.endswith(ext) for ext in included_extensions)]
        img_extensions = ["webp", "jpg", "jpeg"]
        img_filenames = [fn_img for fn_img in os.listdir(relevant_path) if any(
            fn_img.endswith(ext_img) for ext_img in img_extensions)]
        thumb_image = out_folder + img_filenames[0]

        file_path = out_folder + file_names[0]
        video_size = file_size(file_path)
        # thumb = out_folder + "cover.jpg"

        j = await v_url.edit(f"`Preparing to upload video:`\
        \n**{ytdl_data['title']}**\
        \nby *{ytdl_data['uploader']}*")
        await v_url.client.send_file(
            v_url.chat_id,
            file_path,
            supports_streaming=True,
            caption=ytdl_data['title'] + "\n" + f"`{video_size}`",
            thumb=thumb_image,
            progress_callback=lambda d, t: asyncio.get_event_loop(
            ).create_task(
                progress(d, t, v_url, c_time, "Uploading..",
                         f"{ytdl_data['title']}.mp4")))
        os.remove(file_path)
        await asyncio.sleep(DELETE_TIMEOUT)
        os.remove(thumb_image)
        await v_url.delete()
        await j.delete()
    shutil.rmtree(out_folder)


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
