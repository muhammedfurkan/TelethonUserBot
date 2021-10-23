"""
Turkish word meaning. Only Turkish. Coded @By_Azade
"""

import logging

import requests
import urllib3
from bs4 import BeautifulSoup
from userbot import bot
from userbot.util import admin_cmd

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


def searchTureng(word):
    http = urllib3.PoolManager()
    url = "http://www.tureng.com/search/"+word
    try:
        answer = http.request('GET', url)
    except:
        return "No connection"
    soup = BeautifulSoup(answer.data, 'html.parser')
    trlated = '**{}** Kelimesinin Türkçe Anlamı/Anlamları:\n\n'.format(word)
    try:
        table = soup.find('table')
        td = table.findAll('td', attrs={'lang': 'tr'})
        for val in td[0:5]:
            trlated = '{}👉  {}\n'.format(trlated, val.text)
        return trlated
    except:
        return "Sonuç bulunamadı"


def turengsearch(word):
    url = "http://www.tureng.com/search/"+word
    try:
        answer = requests.get(url)
    except:
        return "Bağlantı Hatası"
    soup = BeautifulSoup(answer.content, 'html.parser')
    trlated = '**{}** Kelimesinin Türkçe Anlamı/Anlamları:\n\n'.format(word)
    try:
        table = soup.find('table')
        td = table.findAll('td', attrs={'lang': 'tr'})
        for val in td[0:20]:
            trlated = '{}👉  {}\n'.format(trlated, val.text)
        return trlated
    except:
        return "Sonuç bulunamadı"


def searchTureng_tr(word):
    http = urllib3.PoolManager()
    url = "https://tureng.com/tr/turkce-ingilizce/"+word
    try:
        answer = http.request('GET', url)
    except:
        return "No connection"
    soup = BeautifulSoup(answer.data, 'html.parser')
    trlated = '{} Kelimesinin Anlamı/Anlamları:\n\n'.format(word)
    try:
        table = soup.find('table')
        td = table.find_all('td', attrs={'lang': 'en'})
        # print(td)
        for val in td[0:5]:
            trlated = '{}👉  {}\n'.format(trlated, val.text)
        return trlated
    except:
        return "Sonuç bulunamadı"


@bot.on(admin_cmd(pattern=("tureng ?(.*)")))
async def turen(event):
    input_str = event.pattern_match.group(1)
    result = turengsearch(input_str)
    await event.edit(result)


@bot.on(admin_cmd(pattern=("tur_eng ?(.*)")))
async def turen_(event):
    input_str = event.pattern_match.group(1)
    result = searchTureng_tr(input_str)
    await event.edit(result)


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
