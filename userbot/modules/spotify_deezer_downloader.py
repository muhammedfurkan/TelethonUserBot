""" Spotify / Deezer downloader plugin by @anubisxx | Syntax: .sdd link"""
import asyncio

from telethon.errors.rpcerrorlist import (UserAlreadyParticipantError,
                                          YouBlockedUserError)
from telethon.tl.functions.messages import ImportChatInviteRequest

from userbot import bot
from userbot.util import admin_cmd


@bot.on(admin_cmd(pattern="spoti ?(.*)"))
async def _(event):
    if event.fwd_from:
        return
    d_link = event.pattern_match.group(1)
    if ".com" not in d_link:
        await event.edit("` I need a link to download something pro.`**(._.)**")
    else:
        await event.edit("🎶**Initiating Download!**🎶")
    bot = "@DeezLoadBot"

    async with event.client.conversation("@DeezLoadBot") as conv:
        try:
            await conv.send_message("/start")
            response = await conv.get_response()
            try:
                await event.client(ImportChatInviteRequest('AAAAAFZPuYvdW1A8mrT8Pg'))
            except UserAlreadyParticipantError:
                await asyncio.sleep(0.00000069420)
            await conv.send_message(d_link)
            details = await conv.get_response()
            # await event.client.send_message(event.chat_id, details)
            await conv.get_response()
            songh = await conv.get_response()
            await event.client.send_file(event.chat_id, songh, caption="Kanal Linki:\nhttps://t.me/joinchat/AAAAAE8NqbV48l7ls-pFtQ")
            await event.delete()
        except YouBlockedUserError:
            await event.edit("**Error:** `unblock` @DeezLoadBot `and retry!`")
