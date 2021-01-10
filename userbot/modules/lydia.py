import asyncio
import logging
from time import time

from coffeehouse.api import API
from coffeehouse.exception import CoffeeHouseError as CFError
from coffeehouse.lydia import LydiaAI
from sample_config import Config
from telethon import events
from userbot import bot
from userbot.database.lydiadb import (get_ses, is_chat, list_chat, rem_chat,
                                      set_ses)
from userbot.util import admin_cmd

logging.basicConfig(level=logging.INFO)


if Config.LYDIA_API is not None:
    api_key = Config.LYDIA_API
    # Create the CoffeeHouse API instance
    coffeehouse_api = API(api_key)
    # Create Lydia instance
    lydia_session = LydiaAI(coffeehouse_api)


@bot.on(admin_cmd(pattern="cf"))
async def lydia_enable(event):
    if event.fwd_from:
        return
    if Config.MONGO_DB_URI and Config.LYDIA_API is None:
        await event.edit("Make Sure You've added MONGO_URI and LYDIA_API env vars Correctly.")
        return
    await event.edit("Processing...")
    chat_id = event.chat_id
    is_chatt = await is_chat(chat_id)
    if not is_chatt:
        ses = lydia_session.create_session()
        ses_id = str(ses.id)
        expires = str(ses.expires)
        await set_ses(chat_id, ses_id, expires)
        await event.edit("`AI successfully enabled for this chat!`")
    else:
        await event.edit("`AI successfully already enabled for this chat!`")


@bot.on(admin_cmd(pattern="delcf"))
async def lydia_disable(event):
    if event.fwd_from:
        return
    if Config.MONGO_DB_URI and Config.LYDIA_API is None:
        await event.edit("Make Sure You've added MONGO_URI and LYDIA_API env vars Correctly.")
        return
    await event.edit("Processing...")
    chat_id = event.chat_id
    is_chatt = await is_chat(chat_id)
    if not is_chatt:
        await event.edit("`AI isn't enabled here in the first place!`")
    else:
        await rem_chat(chat_id)
        await event.edit("`AI disabled successfully!`")


@bot.on(admin_cmd(pattern="listcf"))
async def lydia_list(event):
    if event.fwd_from:
        return
    if Config.MONGO_DB_URI and Config.LYDIA_API is None:
        await event.edit("Make Sure You've added MONGO_URI and LYDIA_API env vars Correctly.")
        return
    await event.edit("Processing...")
    msg = "**Auto-Chat:**"
    cur = await list_chat()
    for c in cur:
        msg += "\n__Chat:__ `{}`\n".format(str(c['chat_id']))
    await event.edit(msg)


@bot.on(events.NewMessage())
async def Lydia_bot_update(event):
    if event.fwd_from:
        return
    if not Config.MONGO_DB_URI and not Config.LYDIA_API:
        return
    chat_id = event.chat_id
    is_chatt = await is_chat(chat_id)
    if not is_chatt:
        return
    sesh, exp = await get_ses(chat_id)
    me = await bot.get_me()
    if not event.media and me.id != event.sender_id:
        try:
            if int(exp) < time():
                ses = lydia_session.create_session()
                ses_id = str(ses.id)
                expires = str(ses.expires)
                await set_ses(chat_id, ses_id, expires)
                sesh, exp = await get_ses(chat_id)
        except ValueError:
            pass
        query = event.text
        try:
            async with bot.action(event.chat_id, "typing"):
                rep = lydia_session.think_thought(sesh, query)
                await asyncio.sleep(0.3)
                await event.reply(rep)
        except CFError as e:
            await event.reply(f"Chatbot error: {e} occurred in {chat_id}!")
