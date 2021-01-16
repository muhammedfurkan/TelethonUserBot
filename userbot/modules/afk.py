"""AFK Plugin for TelethonUserBot
Syntax: .afk REASON"""
import asyncio
import datetime
import logging

from sample_config import Config
from telethon import events
from telethon.tl import functions, types
from userbot import bot

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)
USER_AFK = {}
afk_time = None
last_afk_message = {}


@bot.on(events.NewMessage(outgoing=True))
async def set_not_afk(event):
    global USER_AFK
    global afk_time
    global last_afk_message
    me = await bot.get_me()
    if me.id != event.sender_id:
        current_message = event.message.message
        if ".afk" not in current_message and "yes" in USER_AFK:
            try:
                await bot.send_message(
                    Config.PRIVATE_GROUP_BOT_API_ID,
                    "Set AFK mode to False"
                )
            except Exception as e:
                await bot.send_message(
                    event.chat_id,
                    "Please set `PRIVATE_GROUP_BOT_API_ID` " +
                    "for the proper functioning of afk functionality " +
                    "in @Unibot\n\n `{}`".format(str(e)),
                    reply_to=event.message.id,
                    silent=True
                )
            USER_AFK = {}
            afk_time = None


@bot.on(events.NewMessage(pattern=r"\.afk ?(.*)", outgoing=True))
async def _(event):
    if event.fwd_from:
        return
    global USER_AFK
    global afk_time
    global last_afk_message
    global reason
    USER_AFK = {}
    afk_time = datetime.datetime.now()
    last_afk_message = {}
    if not USER_AFK:
        reason = event.pattern_match.group(1)
        last_seen_status = await bot(
            functions.account.GetPrivacyRequest(
                types.InputPrivacyKeyStatusTimestamp()
            )
        )
        if isinstance(last_seen_status.rules, types.PrivacyValueAllowAll):
            afk_time = datetime.datetime.now()
        USER_AFK = f"yes: {reason}"
        if reason != "off":
            await event.edit(f"Set AFK mode to True, and Reason is {reason}")
        else:
            await event.edit("AFK has been disabled.")
            USER_AFK = {}
            afk_time = None
        await asyncio.sleep(5)
        await event.delete()
        try:
            await bot.send_message(
                Config.PRIVATE_GROUP_BOT_API_ID,
                f"Set AFK mode to True, and Reason is {reason}"
            )
        except Exception as e:
            logger.warning(str(e))


@bot.on(events.NewMessage(
    incoming=True,
    func=lambda e: bool(e.mentioned or e.is_private)
))
async def on_afk(event):
    if event.fwd_from:
        return
    global USER_AFK
    global afk_time
    global last_afk_message
    afk_since = "yakın bir zaman"
    current_message_text = event.message.message.lower()
    if "afk" in current_message_text:
        # userbot's should not reply to other userbot's
        # https://core.telegram.org/bots/faq#why-doesn-39t-my-bot-see-messages-from-other-bots
        return False
    if USER_AFK and not (await event.get_sender()).bot:
        if afk_time:
            afk_since = ""
            now = datetime.datetime.now()
            datime_since_afk = now - afk_time
            time = float(datime_since_afk.seconds)
            days = time // (24 * 3600)
            time %= 24 * 3600
            hours = time // 3600
            time %= 3600
            minutes = time // 60
            time %= 60
            seconds = time
            if days == 1:
                afk_since = "**Dün**"
            elif days > 1:
                if days > 6:
                    date = now + \
                        datetime.timedelta(
                            days=-days, hours=-hours, minutes=-minutes)
                    afk_since = date.strftime("%A, %Y %B %m, %H:%I")
                else:
                    wday = now + datetime.timedelta(days=-days)
                    afk_since = wday.strftime('%A')
            elif hours > 1:
                afk_since = f"`{int(hours)} saat {int(minutes)} dakika önce`"
            elif minutes > 0:
                afk_since = f"`{int(minutes)} dakika {int(seconds)} saniye önce`"
            else:
                afk_since = f"`{int(seconds)} saniye önce`"
        msg = None
        message_to_reply = "`Şu anda burada değilim.` " + \
            f"`Yakında mesajına döneceğim`.\n\nSebebi: **{reason}**\n\n(Son Görülme: **{afk_since}**)"\
            if reason \
            else f"**Yakında mesajına döneceğim**\n\n(Son Görülme: **{afk_since}**)"
        msg = await event.reply(message_to_reply)
        await asyncio.sleep(5)
        if event.chat_id in last_afk_message:
            await last_afk_message[event.chat_id].delete()
        last_afk_message[event.chat_id] = msg
