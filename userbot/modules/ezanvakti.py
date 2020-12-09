import json
import logging

import requests

from userbot import bot
from userbot.util import admin_cmd, register

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)

TEMPAT = ''


@bot.on(admin_cmd(pattern=("ezanvakti ?(.*)")))
async def get_adzan(adzan):
    if not adzan.text.startswith("."):
        return ""

    if not adzan.pattern_match.group(1):
        LOKASI = TEMPAT
        if not LOKASI:
            await adzan.edit("Please specify a city or a state.")
            return
    else:
        LOKASI = adzan.pattern_match.group(1)

    url = f'http://muslimsalat.com/{LOKASI}.json?key=bd099c5825cbedb9aa934e255a81a5fc'
    request = requests.get(url)
    result = json.loads(request.text)

    if request.status_code != 200:
        await adzan.edit(f"{result['status_description']}")
        return

    tanggal = result["items"][0]["date_for"]
    lokasi = result["query"]
    lokasi2 = result["country"]
    lokasi3 = result["address"]
    lokasi4 = result["state"]

    subuh = result["items"][0]["fajr"]
    syuruk = result["items"][0]["shurooq"]
    zuhur = result["items"][0]["dhuhr"]
    ashar = result["items"][0]["asr"]
    maghrib = result["items"][0]["maghrib"]
    isya = result["items"][0]["isha"]

    textkirim = (f"⏱  **Tarih ** `{tanggal}`:\n" +
                 f"`{lokasi} | {lokasi2} | {lokasi3} | {lokasi4}`\n\n" +
                 f"**Güneş :** `{subuh}`\n" +
                 f"**İmsak :** `{syuruk}`\n" +
                 f"**Öğle :** `{zuhur}`\n" +
                 f"**İkindi :** `{ashar}`\n" +
                 f"**Akşam :** `{maghrib}`\n" +
                 f"**Yatsı :** `{isya}`\n")

    await adzan.edit(textkirim)
