import logging

import aiohttp
from sample_config import Config
from userbot import bot
from userbot.util import admin_cmd

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(admin_cmd(pattern="stream ?(.*)"))
async def stream(event):
    input_str = event.pattern_match.group(1)
    if input_str and input_str.startswith("http"):
        dat = {
            "login": Config.STREAM_TAPE_LOGIN,
            "key": Config.STREAM_TAPE_KEY
        }
        async with aiohttp.ClientSession() as session:
            resp = await session.post("https://api.streamtape.com/account/info", data=dat)
            myjson = await resp.json()
            if myjson['status'] == 200:
                async with session.post("https://api.streamtape.com/remotedl/add",
                                        data={
                                            "login": Config.STREAM_TAPE_LOGIN,
                                            "key": Config.STREAM_TAPE_KEY,
                                            "url": input_str
                                        }
                                        ) as k:
                    m = await k.json()
                    link = "https://streamtape.com/v/{}".format(
                        m['result']['id'])
                    await event.edit("**Link uploaded, check it out after 1-5 min later:** {}".format(link))
    else:
        await event.edit("There is no link to upload.")
