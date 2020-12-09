"plugin created by https://t.me/By_Azade"
import logging

import requests

from userbot import bot
from userbot.util import admin_cmd, register

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(admin_cmd(pattern="sozluk ?(.*)"))
async def sozluk(event):
    if event.fwd_from:
        return
    word = event.pattern_match.group(1)

    if not word:
        await event.edit("anlamını öğrenmek istediğiniz kelimeyi girin")
    else:
        try:
            r_req = requests.get(
                f"https://api.dictionaryapi.dev/api/v1/entries/tr/{word}")
            r_dec = r_req.json()
            r_dec = r_dec[0]
            meaning = r_dec['meaning']['ad']
            anlamlar = "**{} kelimesinin anlamları:**".format(word.upper())
            ornekler = "**{} kelimesinin örnekleri:**".format(word.upper())
            for j in meaning:
                if "definition" in j:
                    anlamlar += "\n" + "👉  " + j['definition']
                    if "example" in j:
                        ornekler += "\n" + "👉  " + j['example']
            out = anlamlar + "\n\n" + ornekler
            await event.edit(out)
        except:
            await event.edit("hata oluştu")
