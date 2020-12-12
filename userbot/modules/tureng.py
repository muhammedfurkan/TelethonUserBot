
import requests
import urllib3
from bs4 import BeautifulSoup

from userbot import bot
from userbot.util import admin_cmd


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
