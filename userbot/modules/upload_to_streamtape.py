import asyncio
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
        async with aiohttp.ClientSession() as ression:
            stat = "https://api.streamtape.com/remotedl/status"
            async with ression.post(stat,
                                    data={
                                        "login": Config.STREAM_TAPE_LOGIN,
                                        "key": Config.STREAM_TAPE_KEY,
                                        "id": m['result']['id']
                                    }) as r2:
                stat_json = await r2.json()
                if stat_json['result'][m['result']['id']]['status'] != 'finished':
                    await event.edit("`Uploaded to https://streamtape.com/ and getting link. Please wait.`")
                    await asyncio.sleep(60)
                    async with aiohttp.ClientSession() as session:
                        serverf = 'https://api.streamtape.com/file/listfolder'
                        async with session.post(serverf,
                                                data={
                                                    "login": Config.STREAM_TAPE_LOGIN,
                                                    "key": Config.STREAM_TAPE_KEY,
                                                    "folder": "CL0Wh3BaZC4"
                                                }) as r1:
                            final = await r1.json()
                            # print(final)
                            my_link = final['result']['files'][-1]['link']
                            await event.edit("**Link uploaded, check it out after 1-5 min later:** {}".format(my_link))
    else:
        await event.edit("There is no link to upload.")
