import asyncio

from telethon.tl.types import MessageEntityMentionName
from userbot import bot
from userbot.database.fbandb import add_chat_fban, get_fban, remove_chat_fban
from userbot.database.gbandb import add_chat_gban, get_gban, remove_chat_gban
from userbot.util import admin_cmd


@bot.on(admin_cmd(pattern="gban ?(.*)"))
async def gban_all(msg):
    textx = await msg.get_reply_message()
    if textx:
        try:
            banreason = "[userbot] "
            banreason += banreason.join(msg.text.split(" ")[1:])
            if banreason == "[userbot]":
                raise TypeError
        except TypeError:
            banreason = "[userbot] gban"
    else:
        banid = msg.text.split(" ")[1]
        if banid.isnumeric():
            # if its a user id
            banid = int(banid)
        else:
            # deal wid the usernames
            if msg.message.entities is not None:
                probable_user_mention_entity = msg.message.entities[0]

            if isinstance(probable_user_mention_entity,
                          MessageEntityMentionName):
                ban_id = probable_user_mention_entity.user_id
        try:
            banreason = "[userbot] "
            banreason += banreason.join(msg.text.split(" ")[2:])
            if banreason == "[userbot]":
                raise TypeError
        except TypeError:
            banreason = "[userbot] gban"
    if not textx:
        await msg.edit(
            "Reply Message missing! Might fail on many bots! Still attempting Gban!"
        )
        # Ensure User Read the warning
        await asyncio.sleep(1)
    x = (await get_gban())
    count = 0
    banlist = [i["chatid"] for i in x]
    for banbot in banlist:
        async with bot.conversation(banbot) as conv:
            if textx:
                c = await msg.forward_to(banbot)
                await c.reply("/id")
            await conv.send_message(f"/gban {banid} {banreason}")
            resp = await conv.get_response()
            await bot.send_read_acknowledge(conv.chat_id)
            count += 1
            # We cant see if he actually Gbanned. Let this stay for now
            await msg.edit("`Gbanned on " + str(count) + " bots!`")
            await asyncio.sleep(0.2)


@bot.on(admin_cmd(pattern="fban ?(.*)"))
async def fedban_all(msg):

    textx = await msg.get_reply_message()
    if textx:
        try:
            banreason = "[userbot] "
            banreason += banreason.join(msg.text.split(" ")[1:])
            if banreason == "[userbot]":
                raise TypeError
        except TypeError:
            banreason = "[userbot] fban"
    else:
        banid = msg.text.split(" ")[1]
        if banid.isnumeric():
            # if its a user id
            banid = int(banid)
        else:
            # deal wid the usernames
            if msg.message.entities is not None:
                probable_user_mention_entity = msg.message.entities[0]

            if isinstance(probable_user_mention_entity,
                          MessageEntityMentionName):
                ban_id = probable_user_mention_entity.user_id
        try:
            banreason = "[userbot] "
            banreason += banreason.join(msg.text.split(" ")[2:])
            if banreason == "[userbot]":
                raise TypeError
        except TypeError:
            banreason = "[userbot] fban"
        spamwatch = "spam" in banreason
    failed = {}
    count = 1
    x = (await get_fban())
    fbanlist = [i["chatid"] for i in x]
    for bangroup in fbanlist:

        # Send to proof to Spamwatch in case it was spam
        # Spamwatch is a reputed fed fighting against spam on telegram

        if bangroup == -1001312712379:
            if spamwatch:
                if textx:
                    await textx.forward_to(-1001312712379)
                else:
                    await msg.reply(
                        "`Spam message detected. But no reply message, can't forward to SpamWatch.`"
                    )
            continue
        async with bot.conversation(bangroup) as conv:
            await conv.send_message(f"!fban {banid} {banreason}")
            resp = await conv.get_response()
            await bot.send_read_acknowledge(conv.chat_id)
            if "Beginning federation ban " not in resp.text:
                failed[bangroup] = str(conv.chat_id)
            else:
                count += 1
                await msg.edit("`Fbanned on " + str(count) + " feds!`")
            # Sleep to avoid a floodwait.
            # Prevents floodwait if user is a fedadmin on too many feds
            await asyncio.sleep(0.2)
    if failed:
        failedstr = ""
        for i, value in failed.items():
            failedstr += value
            failedstr += " "
        await msg.reply(f"`Failed to fban in {failedstr}`")
    else:
        await msg.reply("`Fbanned in all feds!`")


@bot.on(admin_cmd(pattern="addfban ?(.*)"))
async def add_to_fban(chat):
    await add_chat_fban(chat.chat_id)
    await chat.edit("`Added this chat under the Fbanlist!`")


@bot.on(admin_cmd(pattern="addgban ?(.*)"))
async def add_to_gban(chat):
    await add_chat_gban(chat.chat_id)
    print(chat.chat_id)
    await chat.edit("`Added this bot under the Gbanlist!`")


@bot.on(admin_cmd(pattern="removefban ?(.*)"))
async def remove_from_fban(chat):
    await remove_chat_fban(chat.chat_id)
    await chat.edit("`Removed this chat from the Fbanlist!`")


@bot.on(admin_cmd(pattern="removegban ?(.*)"))
async def remove_from_gban(chat):
    await remove_chat_gban(chat.chat_id)
    await chat.edit("`Removed this bot from the Gbanlist!`")
