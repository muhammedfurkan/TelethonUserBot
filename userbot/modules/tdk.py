"""
Turkish word meaning. Only Turkish. Coded @By_Azade
"""

import logging

import requests

from userbot import bot
from userbot.util import admin_cmd, register

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(admin_cmd(pattern="tdk ?(.*)"))
async def tdk(event):
    if event.fwd_from:
        return
    inp = event.pattern_match.group(1)
    kelime = "https://sozluk.gov.tr/gts?ara={}".format(inp)
    headers = {"USER-AGENT": "Unibot"}
    response = requests.get(kelime, headers=headers).json()

    try:
        anlam_sayisi = response[0]['anlam_say']
        x = "TDK Sözlük **{}**\n\n".format(inp)
        for anlamlar in range(int(anlam_sayisi)):
            x += "👉{}\n".format(response[0]
                                ['anlamlarListe'][anlamlar]['anlam'])
            # print(x)
        await event.edit(x)
    except KeyError:
        await event.edit(KeyError)

# TDK kütüphanesi ile bu şekilde.

# from tdk import tdk

# # create new word
# word = tdk.new_word("test")
# # prints meaning of the word
# test = "\n"
# for a in word.meaning():
#     test += "\n{}".format(a)
# # print(word.meaning())
# print(test)
# # # prints all the word's data
# # print(word.all_data())
