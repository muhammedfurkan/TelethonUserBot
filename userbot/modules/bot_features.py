import asyncio
import logging

from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError

from userbot import bot
from userbot.util import admin_cmd, register

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(admin_cmd(pattern=("sg ?(.*)")))
async def _(event):
    if event.fwd_from:
        return
    if not event.reply_to_msg_id:
        await event.edit("```Reply to any user message.```")
        return
    reply_message = await event.get_reply_message()
    if not reply_message.text:
        await event.edit("```reply to text message```")
        return
    chat = "@SangMataInfo_bot"
    sender = reply_message.sender
    if sender.bot:
        await event.edit("```Reply to actual users message.```")
        return
    await event.edit("```Processing```")
    async with event.client.conversation(chat) as conv:
        try:
            response = conv.wait_event(events.NewMessage(
                incoming=True, from_users=461843263))
            await event.client.forward_messages(chat, reply_message)
            response = await response
        except YouBlockedUserError:
            await event.reply("```Please unblock @sangmatainfo_bot and try again```")
            return
        if response.text.startswith("Forward"):
            await event.edit("```can you kindly disable your forward privacy settings for good?```")
        else:
            await event.edit(f"{response.message.message}")


@bot.on(admin_cmd(pattern=("fakemail ?(.*)")))
async def _(event):
    if event.fwd_from:
        return
    chat = "@fakemailbot"
    command = "/generate"
    await event.edit("```Fakemail Creating, wait```")
    async with event.client.conversation(chat) as conv:
        try:
            m = await event.client.send_message("@fakemailbot", "/generate")
            await asyncio.sleep(5)
            k = await event.client.get_messages(entity="@fakemailbot", limit=1, reverse=False)
            mail = k[0].text
            # print(k[0].text)
        except YouBlockedUserError:
            await event.reply("```Please unblock @fakemailbot and try again```")
            return
        await event.edit(mail)


@bot.on(admin_cmd(pattern=("mailid ?(.*)")))
async def _(event):
    if event.fwd_from:
        return
    chat = "@fakemailbot"
    command = "/id"
    await event.edit("```Fakemail list getting```")
    async with event.client.conversation(chat) as conv:
        try:
            m = await event.client.send_message("@fakemailbot", "/id")
            await asyncio.sleep(5)
            k = await event.client.get_messages(entity="@fakemailbot", limit=1, reverse=False)
            mail = k[0].text
            # print(k[0].text)
        except YouBlockedUserError:
            await event.reply("```Please unblock @fakemailbot and try again```")
            return
        await event.edit(mail)


@bot.on(admin_cmd(pattern=("ub ?(.*)")))
async def _(event):
    if event.fwd_from:
        return
    if not event.reply_to_msg_id:
        await event.edit("```Reply to any user message.```")
        return
    reply_message = await event.get_reply_message()
    if not reply_message.text:
        await event.edit("```reply to text message```")
        return
    chat = "@uploadbot"
    sender = reply_message.sender
    if sender.bot:
        await event.edit("```Reply to actual users message.```")
        return
    await event.edit("```Processing```")
    async with event.client.conversation(chat) as conv:
        try:
            response = conv.wait_event(events.NewMessage(
                incoming=True, from_users=97342984))
            await event.client.forward_messages(chat, reply_message)
            response = await response
        except YouBlockedUserError:
            await event.reply("```Please unblock @uploadbot and try again```")
            return
        if response.text.startswith("Hi!,"):
            await event.edit("```can you kindly disable your forward privacy settings for good?```")
        else:
            await event.edit(f"{response.message.message}")


@bot.on(admin_cmd(pattern=("gid ?(.*)")))
async def _(event):
    if event.fwd_from:
        return
    if not event.reply_to_msg_id:
        await event.edit("```Reply to any user message.```")
        return
    reply_message = await event.get_reply_message()
    if not reply_message.text:
        await event.edit("```reply to text message```")
        return
    chat = "@getidsbot"
    sender = reply_message.sender
    if sender.bot:
        await event.edit("```Reply to actual users message.```")
        return
    await event.edit("```Processing```")
    async with event.client.conversation(chat) as conv:
        try:
            response = conv.wait_event(events.NewMessage(
                incoming=True, from_users=186675376))
            await event.client.forward_messages(chat, reply_message)
            response = await response
        except YouBlockedUserError:
            await event.reply("```you blocked bot```")
            return
        if response.text.startswith("Hello,"):
            await event.edit("```can you kindly disable your forward privacy settings for good?```")
        else:
            await event.edit(f"{response.message.message}")


@bot.on(admin_cmd(pattern="voicy ?(.*)"))
async def voicy(event):
    if event.fwd_from:
        return
    if not event.reply_to_msg_id:
        await event.edit("`Lütfen bir mesaja yanıt verin.`")
        return
    reply_message = await event.get_reply_message()
    if not reply_message.media:
        await event.edit("`Lütfen bir dosyaya yanıt verin.`")
        return
    chat = "@Voicybot"
    sender = reply_message.sender
    if sender.bot:
        await event.edit("`Lütfen gerçekten bir kullanıcının mesajına yanıt verin.`")
        return
    await event.edit("`Ses dinleniyor...`")
    async with event.client.conversation(chat) as conv:
        try:
            await event.client.forward_messages(chat, reply_message)
        except YouBlockedUserError:
            await event.reply(f"`Mmmh sanırım` {chat} `engellemişsin. Lütfen engeli aç.`")
            return

        response = conv.wait_event(events.MessageEdited(
            incoming=True, from_users=259276793))
        response = await response
        if response.text.startswith("__👋"):
            await event.edit("`Botu başlatıp Türkçe yapmanız gerekmektedir.`")
        elif response.text.startswith("__👮"):
            await event.edit("`Ses bozuk, ne dediğini anlamadım.`")
        else:
            await event.edit(f"`{response.text}`")
