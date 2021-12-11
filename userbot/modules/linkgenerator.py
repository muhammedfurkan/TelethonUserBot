import asyncio
from asyncio import TimeoutError, sleep

from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.types import MessageEntityTextUrl as keeper
from userbot import bot
from userbot.util import admin_cmd


@bot.on(admin_cmd(pattern="public ?(.*)"))
async def getlink(file):
    if file.fwd_from:
        return
    if not file.is_reply:
        await file.edit("`Please Reply to a File.`")
    reply = await file.get_reply_message()
    if not reply.media:
        await file.edit("`I can't generate Link for texts!`")
    eris = await file.edit("`Generating a Link for this File`")
    linkbot = "DirectLinkGeneratorbot"
    async with bot.conversation(linkbot) as convo:
        try:
            response = convo.wait_event(events.NewMessage(
                incoming=True, from_users=linkbot,
            ))
            await reply.forward_to(linkbot)
            response = await response
        except YouBlockedUserError:
            await file.edit(
                f"`Unblock @{linkbot} to use this Plugin!`")
        except asyncio.TimeoutError:
            await file.edit(
                "`Bot doesn't seem to be responding.`")
        response_link = response.text
        await bot.send_read_acknowledge(linkbot)
        if response_link.startswith("You need to join"):
            return await eris.edit(f"Please check {linkbot}")
        elif response_link.startswith("**Title:"):
            for link, _ in response.get_entities_text(keeper):
                if isinstance(link, keeper):
                    thelink = link.url
                else:
                    return await eris.edit("Couldn't find any Links")
            file_name = response_link.split("\n", 1)[0].split(":")[
                1].replace("**", "").strip()
            donjo = f"**File Name :** \n{file_name}\n\n"
            donjo += f"**Direct Link :** \n{thelink}"
            return await eris.edit(donjo)
        else:
            return await eris.edit("`Unknown Response!`")
