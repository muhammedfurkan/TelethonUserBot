import asyncio
import logging
import os
from random import choice, randint

import requests
from bs4 import BeautifulSoup as soup
from PIL import Image

from sample_config import Config
from userbot import bot
from userbot.util import admin_cmd

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)

down_p = str(Config.TMP_DOWNLOAD_DIRECTORY.rstrip('/'))


@bot.on(admin_cmd(pattern="wall ?(.*)"))
async def wallp(event):
    if not os.path.isdir(down_p):
        os.makedirs(down_p)
    cat_id = event.chat_id
    input_str = event.pattern_match.group(1)
    if input_str:
        qu = input_str
        await event.edit(f'**Processing...**\n**Searching for **`{qu}`')
        try:
            link = await walld(str(qu))
        except Exception as e:
            await event.edit(e)
            return
        if link:
            idl = await dlimg(link[0])
            if link[0].endswith('png'):
                im = Image.open(idl)
                os.remove(idl)
                idl = idl.replace('png', 'jpeg')
                im = im.convert('RGB')
                im.save(idl, 'jpeg')
            await event.edit('**Uploading...**')
            if len(link[1].split()) >= 11:
                capo = '**' + ' '.join(link[1].split()[:11]) + '**'
            else:
                capo = '**' + link[1] + '**'
            try:
                await event.client.send_file(cat_id, idl, caption=capo)
                await event.client.send_file(cat_id, idl, force_document=True)
                os.remove(idl)
            except Exception as e:
                await event.edit(e)
        else:
            await event.edit('**Result Not Found**')
        await asyncio.sleep(3)
        await event.delete()
    else:
        await event.edit('**Give me Something to search.**')


async def dlimg(link):
    e = requests.get(link).content
    paea = 'donno.{}'.format(link.split('.')[-1])
    path_i = os.path.join(down_p, paea)
    with open(path_i, 'wb') as k:
        k.write(e)
    return path_i


async def walld(strin: str):
    if len(strin.split()) > 1:
        strin = '+'.join(strin.split())
    url = 'https://wall.alphacoders.com/search.php?search='
    none_got = [
        'https://wall.alphacoders.com/finding_wallpapers.php',
        'https://wall.alphacoders.com/search-no-results.php',
    ]

    page_link = 'https://wall.alphacoders.com/search.php?search={}&page={}'
    resp = requests.get(f'{url}{strin}')
    if resp.url in none_got:
        return False
    if 'by_category.php' in resp.url:
        page_link = str(resp.url).replace('&amp;', '') + '&page={}'
        check_link = True
    else:
        check_link = False
    resp = soup(resp.content, 'lxml')
    try:
        page_num = resp.find('div', {'class': 'visible-xs'})
        page_num = page_num.find('input', {'class': 'form-control'})
        page_num = int(page_num['placeholder'].split(' ')[-1])
    except Exception:
        page_num = 1
    n = randint(1, page_num)
    if page_num != 1:
        if check_link:
            resp = requests.get(page_link.format(n))
        else:
            resp = requests.get(page_link.format(strin, n))
        resp = soup(resp.content, 'lxml')
    a_s = resp.find_all('a')
    tit_links = []
    r = ['thumb', '350', 'img', 'big.php?i', 'data-src', 'title']
    list_a_s = [a_tag for a_tag in a_s if all(d in str(a_tag) for d in r)]
    try:
        for df in list_a_s:
            imgi = df.find('img')
            li = str(imgi['data-src']).replace('thumb-350-', '')
            titl = str(df['title']).replace('|', '')
            titl = titl.replace('  ', '')
            titl = titl.replace('Image', '')
            titl = titl.replace('HD', '')
            titl = titl.replace('Wallpaper', '')
            titl = titl.replace('Background', '')
            p = (li, titl)
            tit_links.append(p)
    except Exception:
        pass
    del list_a_s
    if not tit_links:
        return False
    return choice(tit_links)
