import datetime
import json
import logging
from datetime import datetime

import pytz
from userbot import bot
from userbot.bin import namaz_vakti
from userbot.util import admin_cmd

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)

TEMP = ''


@bot.on(admin_cmd(pattern=("ezanv ?(.*) + ?(.*)")))
async def namaz_(event):
    """kullanımı .ezanv <şehir> <ilçe>"""
    if not event.text.startswith("."):
        return ""

    if not event.pattern_match.group(1):
        LOKASYON = TEMP
        if not LOKASYON:
            await event.edit("Please specify a city or a state.")
            return
    else:
        LOKASYON = event.pattern_match.group(1)
        if LOKASYON:
            LOKASYON = LOKASYON.replace('i', 'İ').upper()

        # LOKASYON = LOKASYON.encode().decode('UTF-8').upper()
    # await event.edit("ezan vakti diyanetten alınıyor.")
    if not event.pattern_match.group(2):
        await event.edit("ilçe giriniz. doğru format `.ezanv <şehir> <ilçe>`")
    else:
        LOKASYON_2 = event.pattern_match.group(2)
        if LOKASYON_2:
            LOKASYON_2 = LOKASYON_2.replace('i', 'İ').upper()
    yer = './userbot/bin/namaz_vakti/db/yerler.ndb'
    with open(yer, "r", encoding="utf-8") as f:
        yerler_json = json.load(f)
    namaz = namaz_vakti.namazvakti()
    sehirler_sonuc = namaz.sehirler(2)
    sonuc_sehirler = {v: k for k, v in sehirler_sonuc['veri'].items()}
    sehir_id = sonuc_sehirler[LOKASYON]
    ilceler_sonuc = namaz.ilceler(2, sehir_id)
    sonuc_ilceler = {v: k for k, v in ilceler_sonuc['veri'].items()}
    sonuc_str = sonuc_ilceler[LOKASYON_2]
    sonuc = namaz.vakit(sonuc_str)

    tz = pytz.timezone('Europe/Istanbul')
    istanbul_now = datetime.now(tz)
    bugun = istanbul_now.strftime("%d%m%Y")

    gun = bugun[:2]
    ay = bugun[2:4]
    yil = bugun[4:]
    tam_gun = f'{gun}.{ay}.{yil}'
    yer = sonuc['veri']['yer_adi']
    if sonuc['veri']['vakit']['tarih'] == tam_gun:
        # print("tru")
        tarih = sonuc['veri']['vakit']['uzun_tarih']
        hicri_tarih = sonuc['veri']['vakit']['hicri_uzun']
        imsak = sonuc['veri']['vakit']['imsak']
        gunes = sonuc['veri']['vakit']['gunes']
        ogle = sonuc['veri']['vakit']['ogle']
        ikindi = sonuc['veri']['vakit']['ikindi']
        aksam = sonuc['veri']['vakit']['aksam']
        yatsi = sonuc['veri']['vakit']['yatsi']
    out = ("**Diyanet Namaz Vakitleri**\n\n" +
           f"📍**Yer: ** `{yer}`\n" +
           f"🗓**Tarih ** `{tarih}`\n" +
           f"🌕**Hicri Tarih :** `{hicri_tarih}`\n" +
           f"🏙**İmsak :** `{imsak}`\n" +
           f"🌅**Güneş :** `{gunes}`\n" +
           f"🌇**Öğle :** `{ogle}`\n" +
           f"🌆**İkindi :** `{ikindi}`\n" +
           f"🌃**Akşam :** `{aksam}`\n" +
           f"🌌**Yatsı :** `{yatsi}`\n"
           )
    await event.edit(out)
