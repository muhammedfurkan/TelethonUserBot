"""Log PMs
Check https://t.me/tgbeta/3505"""
import logging
import os
import sys

from sample_config import Config
from telethon import events
from userbot import bot

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.WARN)
NO_PM_LOG_USERS = []


@bot.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def monito_p_m_s(event):
    sender = await event.get_sender()
    me = await bot.get_me()
    if Config.NC_LOG_P_M_S and not sender.bot:
        chat = await event.get_chat()
        if chat.id not in NO_PM_LOG_USERS and chat.id != me.id:
            try:
                e = await event.client.get_entity(Config.PM_LOGGR_BOT_API_ID)
                await event.client.forward_messages(
                    e, event.message or event.media, silent=True
                )

            except Exception as e:
                # logger.warning(str(e))
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                print(e)
