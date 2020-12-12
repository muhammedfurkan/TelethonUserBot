"download from soundcloud mp3 using telegram. Credits: https://t.me/By_Azade"
import logging
import os

from sclib.asyncio import SoundcloudAPI, Track

from sample_config import Config
from userbot import bot
from userbot.util import admin_cmd

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(admin_cmd(pattern="scdl ?(.*)"))  # pylint:disable=E0602
async def _(event):
    if event.fwd_from:
        return
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    msg = await event.edit("`Music downloading from SoundCloud, please wait..`")
    link = event.pattern_match.group(1)
    if os.path.exists(Config.TMP_DOWNLOAD_DIRECTORY):
        api = SoundcloudAPI()
        track = await api.resolve(link)
        if type(track) is not Track:
            raise AssertionError
        filename = Config.TMP_DOWNLOAD_DIRECTORY + \
            f'{track.artist} - {track.title}.mp3'
        with open(filename, 'wb+') as fp:
            await track.write_mp3_to(fp)
        edited = await msg.edit("`Downloaded. Uploading now..`")
        await event.client.send_file(
            event.chat_id,
            filename,
            force_document=True,
            supports_streaming=True,
            allow_cache=False,
            reply_to=event.message.id,
            caption=track.title
        )
        await edited.delete()
        os.remove(Config.TMP_DOWNLOAD_DIRECTORY +
                  f'{track.artist} - {track.title}.mp3')
        os.removedirs(Config.TMP_DOWNLOAD_DIRECTORY)
