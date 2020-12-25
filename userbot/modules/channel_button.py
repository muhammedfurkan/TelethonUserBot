""" channel buttons bot for spesific channel/channels Coded By https://t.me/By_Azade"""

from sample_config import Config
from telethon import custom, events
from telethon.tl.custom import Button
from sample_config import Config
from userbot import tgbot
from telethon.tl.types import PeerUser
global data 
data = 0
global data_1
data_1 = 0
global data_2
data_2 = 0

@tgbot.on(events.CallbackQuery())
async def test(event):
    channel = -1001477006210
    global data
    global data_1
    global data_2
    # name = get_display_name(event.original_update.user_id)
    name    = await bot.get_entity(PeerUser(event.original_update.user_id))
    msg = f"[{name.first_name}](tg://user?id={name.id})"
    # message_link = f"tg://openmessage?chat_id={event.original_update.peer.channel_id}&message_id={event.original_update.msg_id}"
    message_link = f"https://t.me/c/{event.original_update.peer.channel_id}/{event.original_update.msg_id}"
    if event.data.decode('utf-8') == "up":
        data += 1
        buton = tgbot.build_reply_markup(
            [
                Button.inline(f"👍 {data}" , data="up"), 
                Button.inline(f"❤️ {data_1}" , data="kalp"),
                Button.inline(f"😢 {data_2}" , data"agla")
            ]
        )
        await tgbot.edit_message(channel, event.original_update.msg_id, buttons=buton)
        await bot.send_message(-443785781",f"Tıklayan: {msg}, 👍 e tıkladı.\n\nMesaja git: {message_link}")
        # data += 1


    if event.data.decode('utf-8') == "kalp":
        data_1 += 1
        buton = tgbot.build_reply_markup(
            [
                Button.inline(f"👍 {data}" , data="up"), 
                Button.inline(f"❤️ {data_1}" , data="kalp"),
                Button.inline(f"😢 {data_2}" , data"agla")
            ]
        )
        await tgbot.edit_message(channel, event.original_update.msg_id, buttons=buton)
        await bot.send_message(-443785781",f"Tıklayan: {msg}, ❤️ e tıkladı.\n\nMesaja git: {message_link}")
        # data_1 += 1
        
     if event.data.decode('utf-8') == "agla":
        data_2 += 1
        buton = tgbot.build_reply_markup(
            [
                Button.inline(f"👍 {data}" , data="up"), 
                Button.inline(f"❤️ {data_1}" , data="kalp"),
                Button.inline(f"😢 {data_2}" , data"agla")
            ]
        )
        await tgbot.edit_message(channel, event.original_update.msg_id, buttons=buton)
        await bot.send_message(-443785781",f"Tıklayan: {msg}, 😢 e tıkladı.\n\nMesaja git: {message_link}")
        # data_2 += 1

@borg.on(events.NewMessage(chats=-1001477006210))
async def all_messages_catcher(event):
    channel = -1001477006210
    if channel:
        buton = tgbot.build_reply_markup(
            [
                Button.inline(f"👍 {data}" , data="up"), 
                Button.inline(f"❤️ {data_1}" , data="kalp"),
                Button.inline(f"😢 {data_2}" , data"agla")
            ]
        )
        chat = await event.get_chat()
        admin = chat.admin_rights
        if admin:
            await tgbot.edit_message(channel, event.message.id, buttons=buton)
