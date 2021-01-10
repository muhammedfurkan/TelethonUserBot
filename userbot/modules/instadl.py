""" a instagram post downloader plugin for @theUserge. """
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.
import asyncio
import logging
import os
import re
import shlex
import shutil
from os.path import basename
from typing import Optional, Tuple

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from instaloader import (BadCredentialsException, ConnectionException,
                         Instaloader, InvalidArgumentException,
                         LoginRequiredException, NodeIterator, Post, Profile,
                         TwoFactorAuthRequiredException)
from natsort import natsorted
from PIL import Image
from sample_config import Config
from telethon import errors, events
from telethon.tl.types import (DocumentAttributeVideo, InputMediaDocument,
                               InputMediaPhoto)
from userbot import bot
from userbot.util import admin_cmd

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)

thumb_path_ = Config.TMP_DOWNLOAD_DIRECTORY + "/thumb_image.jpg"


async def take_screen_shot(video_file: str, duration: int, path: str = '') -> Optional[str]:
    """ take a screenshot """
    logger.info(
        '[[[Extracting a frame from %s ||| Video duration => %s]]]', video_file, duration)
    ttl = duration // 2
    thumb_image_path = path or os.path.join(
        Config.TMP_DOWNLOAD_DIRECTORY, f"{basename(video_file)}.jpg")
    command = f'''ffmpeg -ss {ttl} -i "{video_file}" -vframes 1 "{thumb_image_path}"'''
    err = (await runcmd(command))[1]
    if err:
        logger.error(err)
    return thumb_image_path if os.path.exists(thumb_image_path) else None


async def runcmd(cmd: str) -> Tuple[str, str, int, int]:
    """ run command in terminal """
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(*args,
                                                   stdout=asyncio.subprocess.PIPE,
                                                   stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    return (stdout.decode('utf-8', 'replace').strip(),
            stderr.decode('utf-8', 'replace').strip(),
            process.returncode,
            process.pid)


async def get_thumb(path: str = ''):
    if os.path.exists(thumb_path_):
        return thumb_path_
    if path:
        types = (".jpg", ".webp", ".png")
        if path.endswith(types):
            return None
        file_name = os.path.splitext(path)[0]
        for type_ in types:
            thumb_path = file_name + type_
            if os.path.exists(thumb_path):
                if type_ != ".jpg":
                    new_thumb_path = f"{file_name}.jpg"
                    Image.open(thumb_path).convert(
                        'RGB').save(new_thumb_path, "JPEG")
                    os.remove(thumb_path)
                    thumb_path = new_thumb_path
                return thumb_path
        metadata = extractMetadata(createParser(path))
        if metadata and metadata.has("duration"):
            return await take_screen_shot(
                path, metadata.get("duration").seconds)
    # if os.path.exists(LOGO_PATH):
    #     return LOGO_PATH
    return None


async def remove_thumb(thumb: str) -> None:
    if thumb and os.path.exists(thumb) and thumb != thumb_path_:
        os.remove(thumb)


def get_lst_of_files(input_directory, output_lst):
    filesinfolder = os.listdir(input_directory)
    for file_name in filesinfolder:
        if not file_name.endswith(".txt"):
            current_file_name = os.path.join(input_directory, file_name)
            if os.path.isdir(current_file_name):
                return get_lst_of_files(current_file_name, output_lst)
            output_lst.append(current_file_name)
    return output_lst


def get_caption(post: Post) -> str:
    """ adds link to profile for tagged users """
    caption = post.caption
    replace = '<a href="https://instagram.com/{}/">{}</a>'
    for mention in post.caption_mentions:
        men = '@' + mention
        val = replace.format(mention, men)
        caption = caption.replace(men, val)
    header = f'♥️`{post.likes}`  💬`{post.comments}`'
    if post.is_video:
        header += f'  👀`{post.video_view_count}`'
    caption = header + '\n\n' + (caption or '')
    return caption


async def upload_to_tg(event, dirname: str, post: Post) -> None:    # pylint: disable=R0912
    """ uploads downloaded post from local to telegram servers """
    pto = (".jpg", ".jpeg", ".png", ".bmp")
    vdo = (".mkv", ".mp4", ".webm")
    paths = []
    if post.typename == 'GraphSidecar':
        # upload media group
        captioned = False
        media = []
        for path in natsorted(os.listdir(dirname)):
            ab_path = dirname + '/' + path
            paths.append(ab_path)
            if str(path).endswith(pto):
                if not captioned:
                    captioned = True
                media.append(InputMediaPhoto(ab_path))
            elif str(path).endswith(vdo):
                if not captioned:
                    captioned = True
                media.append(InputMediaDocument(ab_path))
        if media:
            mdia = get_lst_of_files(dirname, [])
            await bot.send_file(entity=event.chat_id, file=mdia)

    if post.typename == 'GraphImage':
        # upload a photo
        for path in natsorted(os.listdir(dirname)):
            if str(path).endswith(pto):
                ab_path = dirname + '/' + path
                paths.append(ab_path)
                await event.client.send_file(
                    event.chat_id,
                    ab_path,
                    caption=get_caption(post)[:1023])
                # await event.client.send_fie(
                #     Config.PRIVATE_GROUP_BOT_API_ID,
                #     ab_path,
                #     caption=get_caption(post)[:1023])

    if post.typename == 'GraphVideo':
        # upload a video
        for path in natsorted(os.listdir(dirname)):
            if str(path).endswith(vdo):
                ab_path = dirname + '/' + path
                paths.append(ab_path)
                thumb = await get_thumb(ab_path)
                duration = 0
                width = 0
                height = 0
                metadata = extractMetadata(createParser(ab_path))
                if metadata.has("width"):
                    width = metadata.get("width")
                if metadata.has("height"):
                    height = metadata.get("height")
                if metadata and metadata.has("duration"):
                    duration = metadata.get("duration").seconds

                await event.client.send_file(
                    entity=event.chat.id,
                    file=ab_path,
                    attributes=[
                        DocumentAttributeVideo(
                            duration=duration,
                            w=width,
                            h=height,
                            round_message=False,
                            supports_streaming=True)
                    ],
                    thumb=thumb,
                    caption=get_caption(post)[:1023])
                # await event.client.send_file(
                #     entiy=Config.PRIVATE_GROUP_BOT_API_ID,
                #     file=ab_path,
                #     attributes=[
                #         DocumentAttributeVideo(
                #             duration=duration,
                #             w=width,
                #             h=height,
                #             round_message=False,
                #             supports_streaming=True)
                #     ],
                #     thumb=thumb,
                #     caption=get_caption(post)[:1023])
                await remove_thumb(thumb)
    for del_p in paths:
        if os.path.lexists(del_p):
            os.remove(del_p)


# run some process in threads?

def download_post(client: Instaloader, post: Post) -> bool:
    """ Downloads content and returns True """
    client.download_post(post, post.owner_username)
    return True


def get_post(client: Instaloader, shortcode: str) -> Post:
    """ returns a post object """
    return Post.from_shortcode(client.context, shortcode)


def get_profile(client: Instaloader, username: str) -> Profile:
    """ returns profile """
    return Profile.from_username(client.context, username)


def get_profile_posts(profile: Profile) -> NodeIterator[Post]:
    """ returns a iterable Post object """
    return profile.get_posts()


@bot.on(admin_cmd(pattern="postdl ?(.*)"))
async def _insta_post_downloader(event):
    """ download instagram post """
    await event.edit('`Setting up Configs. Please don\'t flood.`')
    dirname = 'instadl_{target}'
    filename = '{target}\'s_post'
    insta = Instaloader(
        dirname_pattern=dirname,
        filename_pattern=filename,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False
    )
    if Config.INSTA_ID and Config.INSTA_PASS:
        # try login
        try:
            insta.load_session_from_file(Config.INSTA_ID)
            await event.edit('`Logged in with current Session`')
        except FileNotFoundError:
            await event.edit('`Login required. Trying to login`')
            try:
                insta.login(Config.INSTA_ID, Config.INSTA_PASS)
            except InvalidArgumentException:
                logger.error('Provided `INSTA_ID` is incorrect')
                return
            except BadCredentialsException:
                logger.error('Provided `INSTA_PASS` is incorrect')
                return
            except ConnectionException:
                logger.error('Instagram refused to connect. Try again later or never'
                             ' (your choice)😒')
                return
            # This is a nightmare.
            except TwoFactorAuthRequiredException:
                # Send a promt for 2FA code in saved messages
                chat_type = 'Saved Messages'
                text = ('[**2 Factor Authentication Detected**]\n'
                        f'I have sent a message to {chat_type}. '
                        'Please continue there and send your 2FA code.')
                await event.edit(text)
                for _ in range(4):
                    # initial convo with the user who sent message in pm.
                    # if user is_self convo in saved messages
                    # else in pm of sudo user
                    async with event.client.conversation(event.chat_id) as asker:
                        asked = await asker.send_message('Please reply me with your 2FA code `int`')
                        response = await asker.wait_event(events.NewMessage(
                            incoming=True, from_users=event.chat_id))
                        if not response.text:
                            # I said reply me.
                            continue
                        code = response.text
                        if not (code.isdigit() and len(code) == 6):
                            # the six digit code
                            # What else it has always been a six digit code.
                            continue
                        try:
                            insta.two_factor_login(code)
                            break
                        except BadCredentialsException as b_c_e:
                            await asker.edit(b_c_e)
                        except InvalidArgumentException:
                            await asked.edit('`No pending Login Found`')
                            return
            else:
                try:
                    insta.save_session_to_file()
                except LoginRequiredException:
                    logger.error(
                        'Failed to save session file, probably due to invalid login.')
                    await asyncio.sleep(5)
    else:
        await event.edit('Login Credentials not found.\n`[NOTE]`: '
                         '**You may not be able to download private contents or so**')
        await asyncio.sleep(2)

    p = r'^(?:https?:\/\/)?(?:www\.)?(?:instagram\.com.*\/(p|tv|reel)\/)([\d\w\-_]+)(?:\/)?(\?.*)?$'
    match = re.search(p, event.pattern_match.group(1))
    if match:
        dtypes = {
            'p': 'POST',
            'tv': 'IGTV',
            'reel': 'REELS'
        }
        d_t = dtypes.get(match.group(1))
        if not d_t:
            logger.error('Unsupported Format')
            return
        sent = await event.edit(f'`Fetching {d_t} Content.`')
        shortcode = match.group(2)
        post = get_post(insta, shortcode)
        try:
            download_post(insta, post)
            await upload_to_tg(event, dirname.format(target=post.owner_username), post)
        except (KeyError, LoginRequiredException):
            logger.error("Post is private. Login and try again")
            return
        except errors.FloodWaitError:
            await asyncio.sleep(15)
            await upload_to_tg(event, dirname.format(target=post.owner_username), post)
        finally:
            shutil.rmtree(dirname.format(
                target=post.owner_username), ignore_errors=True)
        await sent.delete()
    else:
        logger.error('`Invalid Input`')
