import logging

import requests
from bs4 import BeautifulSoup

from userbot import bot
from userbot.util import admin_cmd

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(admin_cmd(pattern="hava ?(.*)"))
async def hava(event):
    if event.fwd_from:
        return
    sehir = event.pattern_match.group(1)
    try:
        mesaj = havaDurumu(sehir)
    except Exception as hata:
        mesaj = f"**Uuppss:**\n\n`{hata}`"
    try:
        await event.edit(mesaj)
    except Exception as hata:
        await event.edit(f"**Uuppss:**\n\n`{hata}`")


def havaDurumu(sehir):
    url = f"https://www.google.com/search?&q={sehir} hava durumu" + \
        "&lr=lang_tr&hl=tr"
    kimlik = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}

    istek = requests.get(url, kimlik)
    corba = BeautifulSoup(istek.text, "lxml")

    gun_durum = corba.findAll('div', class_='BNeawe')
    gun, durum = gun_durum[3].text.strip().split('\n')
    derece = corba.find('div', class_='BNeawe').text

    return f"**{sehir.capitalize()}**\n\t__{gun}__\n\t\t`{durum} {derece}`"
