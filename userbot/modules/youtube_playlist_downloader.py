# """
# Audio and video downloader using Youtube-dl
# .yta To Download in mp3 format
# .ytv To Download in mp4 format
# """
# import asyncio
# import logging
# import os
# import shutil
# import time

# from hachoir.metadata import extractMetadata
# from hachoir.parser import createParser
# from sample_config import Config
# from telethon.tl.types import DocumentAttributeVideo
# from userbot import bot
# from userbot.util import admin_cmd, progress

# from youtube_dl import YoutubeDL
# from youtube_dl.utils import (ContentTooShortError, DownloadError,
#                               ExtractorError, GeoRestrictedError,
#                               MaxDownloadsReached, PostProcessingError,
#                               UnavailableVideoError, XAttrMetadataError)

# logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
#                     level=logging.WARNING)
# logger = logging.getLogger(__name__)


# DELETE_TIMEOUT = 5


# @bot.on(admin_cmd(pattern="playlist(a|v) (.*)"))
# async def download_video(v_url):
#     """ For .ytdl command, download media from YouTube and many other sites. """
#     url = v_url.pattern_match.group(2)
#     type = v_url.pattern_match.group(1).lower()
#     await v_url.edit("`Preparing to download...`")
#     out_folder = Config.TMP_DOWNLOAD_DIRECTORY + "youtubedl/"
#     thumb_image_path = Config.TMP_DOWNLOAD_DIRECTORY + "/thumb_image.jpg"
#     if not os.path.isdir(out_folder):
#         os.makedirs(out_folder)
#     if type == "a":
#         opts = {
#             'format': 'bestaudio',
#             'addmetadata': True,
#             'noplaylist': False,
#             'key': 'FFmpegMetadata',
#             'writethumbnail': True,
#             'embedthumbnail': True,
#             'prefer_ffmpeg': True,
#             'geo_bypass': True,
#             'nocheckcertificate': True,
#             'postprocessors': [{
#                 'key': 'FFmpegExtractAudio',
#                 'preferredcodec': 'mp3',
#                 'preferredquality': '320',
#             }],
#             'outtmpl': out_folder + '%(title)s.%(ext)s',
#             'quiet': True,
#             'logtostderr': False
#         }
#         video = False
#         song = True

#     elif type == "v":
#         opts = {
#             'format': 'best',
#             'addmetadata': True,
#             'noplaylist': False,
#             'getthumbnail': True,
#             'embedthumbnail': True,
#             'xattrs': True,
#             'writethumbnail': True,
#             'key': 'FFmpegMetadata',
#             'prefer_ffmpeg': True,
#             'geo_bypass': True,
#             'nocheckcertificate': True,
#             'postprocessors':
#             [{
#                 'key': 'FFmpegVideoConvertor',
#                 'preferedformat': 'mp4'},
#              ],
#             'outtmpl': out_folder + '%(title)s.%(ext)s',
#             'logtostderr': False,
#             'quiet': True
#         }
#         song = False
#         video = True

#     try:
#         await v_url.edit("`Fetching playlist data, please wait..`")
#         with YoutubeDL(opts) as ytdl:
#             ytdl_data = ytdl.extract_info(url)
#             # print(ytdl_data['thumbnail'])
#         filename = sorted(get_lst_of_files(out_folder, []))
#     except DownloadError as DE:
#         await v_url.edit(f"`{str(DE)}`")
#         return
#     except ContentTooShortError:
#         await v_url.edit("`The download content was too short.`")
#         return
#     except GeoRestrictedError:
#         await v_url.edit(
#             "`Video is not available from your geographic location due to geographic restrictions imposed by a website.`"
#         )
#         return
#     except MaxDownloadsReached:
#         await v_url.edit("`Max-downloads limit has been reached.`")
#         return
#     except PostProcessingError:
#         await v_url.edit("`There was an error during post processing.`")
#         return
#     except UnavailableVideoError:
#         await v_url.edit("`Media is not available in the requested format.`")
#         return
#     except XAttrMetadataError as XAME:
#         await v_url.edit(f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`")
#         return
#     except ExtractorError:
#         await v_url.edit("`There was an error during info extraction.`")
#         return
#     except Exception as e:
#         await v_url.edit(f"{str(type(e)): {str(e)}}")
#         return
#     c_time = time.time()
#     await v_url.edit("`YouTube Playlist Downloading Processing Now.\nPlease Wait!`")
#     if song:
#         for single_file in filename:
#             if os.path.exists(single_file):
#                 caption_rts = os.path.basename(single_file)
#                 force_document = True
#                 supports_streaming = False
#                 document_attributes = []
#                 if single_file.endswith((".mp4", ".mp3", ".flac", ".webm")):
#                     metadata = extractMetadata(createParser(single_file))
#                     duration = 0
#                     width = 0
#                     height = 180
#                     if metadata.has("duration"):
#                         duration = metadata.get('duration').seconds
#                         document_attributes = [
#                             DocumentAttributeVideo(
#                                 duration=duration,
#                                 w=width,
#                                 h=height,
#                                 round_message=False,
#                                 supports_streaming=True,
#                             )
#                         ]
#                     try:
#                         ytdl_data_name_audio = os.path.basename(single_file)
#                         thumb = out_folder + \
#                             ytdl_data_name_audio[:(
#                                 len(ytdl_data_name_audio)-4)] + ".jpg"
#                         print(ytdl_data_name_audio)
#                         file_path = single_file
#                         song_size = file_size(file_path)
#                         await v_url.client.send_file(
#                             v_url.chat_id,
#                             single_file,
#                             caption=f"`{ytdl_data_name_audio}`" +
#                             "\n" + f"{song_size}",
#                             force_document=force_document,
#                             supports_streaming=supports_streaming,
#                             allow_cache=False,
#                             thumb=thumb,
#                             reply_to=v_url.message.id,
#                             attributes=document_attributes,
#                             progress_callback=lambda d, : asyncio.get_event_loop(
#                             ).create_task(
#                                 progress(d, v_url, c_time, "Uploading..",
#                                          f"{ytdl_data_name_audio}")))
#                         # os.remove(thumb)
#                     except Exception as e:
#                         await v_url.client.send_message(
#                             v_url.chat_id,
#                             "{} caused `{}`".format(caption_rts, str(e)),
#                         )
#                         continue
#                     os.remove(single_file)
#                     await asyncio.sleep(DELETE_TIMEOUT)
#                     # await v_url.delete()
#         shutil.rmtree(out_folder)
#     if video:
#         for single_file in filename:
#             if os.path.exists(single_file):
#                 caption_rts = os.path.basename(single_file)
#                 force_document = False
#                 supports_streaming = True
#                 document_attributes = []
#                 if single_file.endswith((".mp4", ".mp3", ".flac", ".webm")):
#                     metadata = extractMetadata(createParser(single_file))
#                     duration = 0
#                     width = 0
#                     height = 0
#                     if metadata.has("duration"):
#                         duration = metadata.get('duration').seconds
#                         document_attributes = [
#                             DocumentAttributeVideo(
#                                 duration=duration,
#                                 w=width,
#                                 h=height,
#                                 round_message=False,
#                                 supports_streaming=True,
#                             )
#                         ]
#                     # print(ytdl_data)
#                     # for file in os.listdir("./DOWNLOADS/youtubedl/"):
#                     #     if file.endswith(".jpg"):
#                     #         thumb = "./DOWNLOADS/youtubedl/" + file
#                         # print(os.path.join("./DOWNLOADS/youtubedl/", file))
#                     # image_link = ytdl_data['thumbnail']
#                     # downloaded_image = wget.download(image_link,out_folder)
#                     # thumb = ytdl_data_name_video + ".jpg"
#                     file_path = single_file
#                     video_size = file_size(file_path)
#                     try:
#                         ytdl_data_name_video = os.path.basename(single_file)
#                         thumb = out_folder + \
#                             ytdl_data_name_video[:(
#                                 len(ytdl_data_name_video)-4)] + ".jpg"
#                         await v_url.client.send_file(
#                             v_url.chat_id,
#                             single_file,
#                             caption=f"`{ytdl_data_name_video}`" +
#                             "\n" + f"{video_size}",
#                             force_document=force_document,
#                             supports_streaming=supports_streaming,
#                             thumb=thumb,
#                             allow_cache=False,
#                             reply_to=v_url.message.id,
#                             attributes=document_attributes,
#                             progress_callback=lambda d, t: asyncio.get_event_loop(
#                             ).create_task(
#                                 progress(d, t, v_url, c_time, "Uploading..",
#                                          f"{ytdl_data_name_video}")))
#                         # os.remove(thumb)
#                     except Exception as e:
#                         await v_url.client.send_message(
#                             v_url.chat_id,
#                             "{} caused `{}`".format(caption_rts, str(e)),
#                         )
#                         continue
#                     os.remove(single_file)
#                     await asyncio.sleep(DELETE_TIMEOUT)
#                     # await v_url.delete()
#         shutil.rmtree(out_folder)


# def get_lst_of_files(input_directory, output_lst):
#     filesinfolder = os.listdir(input_directory)
#     for file_name in filesinfolder:
#         current_file_name = os.path.join(input_directory, file_name)
#         if os.path.isdir(current_file_name):
#             return get_lst_of_files(current_file_name, output_lst)
#         output_lst.append(current_file_name)
#     return output_lst


# def convert_bytes(num):
#     """
#     this function will convert bytes to MB.... GB... etc
#     """
#     for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
#         if num < 1024.0:
#             return "%3.1f %s" % (num, x)
#         num /= 1024.0


# def file_size(file_path):
#     """
#     this function will return the file size
#     """
#     if os.path.isfile(file_path):
#         file_info = os.stat(file_path)
#         return convert_bytes(file_info.st_size)
