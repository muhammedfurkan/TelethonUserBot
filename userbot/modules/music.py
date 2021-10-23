"get music from .m <music query>  Credits https://t.me/By_Azade"
import asyncio
import logging

from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from userbot import bot
from userbot.util import admin_cmd, humanbytes

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(admin_cmd(pattern="music ?(.*)"))  # pylint:disable=E0602
async def music_find(event):
    if event.fwd_from:
        return

    music_name = event.pattern_match.group(1)
    msg = await event.get_reply_message()
    if music_name:
        await event.delete()
        song_result = await event.client.inline_query("deezermusicbot", music_name)

        await song_result[0].click(
            event.chat_id,
            reply_to=event.reply_to_msg_id,
            hide_via=True
        )
    elif msg:
        await event.delete()
        song_result = await event.client.inline_query("deezermusicbot", msg.message)

        await song_result[0].click(
            event.chat_id,
            reply_to=event.reply_to_msg_id,
            hide_via=True
        )


@bot.on(admin_cmd(pattern="spotbot ?(.*)"))  # pylint:disable=E0602
async def _(event):
    if event.fwd_from:
        return
    msg = await event.get_reply_message()
    await event.delete()

    music_name = event.pattern_match.group(1)
    msg = await event.get_reply_message()
    if music_name:
        await event.delete()
        song_result = await event.client.inline_query("spotify_to_mp3_bot", music_name)

        for item_ in song_result:

            if (
                "(FLAC)" in item_.title
                or "(MP3_320)" in item_.title
                or "(MP3_128)" in item_.title
            ):

                j = await item_.click(
                    event.chat_id,
                    reply_to=event.reply_to_msg_id,
                    hide_via=True,
                )

                k = await event.respond(j)
                await j.delete()
                await k.edit("Kanal Linki:\nhttps://t.me/joinchat/AAAAAE8NqbV48l7ls-pFtQ")

    elif msg:

        await event.delete()
        song_result = await event.client.inline_query("spotify_to_mp3_bot", msg.message)
        for item in song_result:

            if (
                "(FLAC)" in item.title
                or "(MP3_320)" in item.title
                or "(MP3_128)" in item.title
            ):

                j = await item.click(
                    event.chat_id,
                    reply_to=event.reply_to_msg_id,
                    hide_via=True,
                )

                k = await event.respond(j)
                await j.delete()
                await k.edit("Kanal Linki:\nhttps://t.me/joinchat/AAAAAE8NqbV48l7ls-pFtQ")


@bot.on(admin_cmd(pattern="audioyt ?(.*)", outgoing=True))
async def _(event):
    if event.fwd_from:
        return
    music_link = event.pattern_match.group(1)
    if music_link:
        chat = "@YTAudioBot"
        async with event.client.conversation(chat) as conv:
            await conv.send_message(music_link)
            await asyncio.sleep(2)
            response = conv.wait_event(events.NewMessage(
                incoming=True, from_users=507379365))
            await event.client.send_message(chat, music_link)
            response = await response
        await event.delete()
        if response.message.media:
            await event.client.send_message(event.chat_id, response)
    else:
        reply_message = await event.get_reply_message()
        chat = "@YTAudioBot"
        sender = reply_message.sender
        await event.edit("```Processing```")
        async with event.client.conversation(chat) as conv:
            response = conv.wait_event(events.NewMessage(
                incoming=True, from_users=507379365))
            await event.client.send_message(chat, reply_message)
            response = await response
            await event.delete()
            if response.message.media:
                await event.client.send_file(event.chat_id, response.message.media)


@bot.on(admin_cmd(pattern="fm ?(.*)"))  # pylint:disable=E0602
async def _(event):
    msg = await event.get_reply_message()
    await event.delete()
    if msg:
        msj = f"[{msg.file.name}](https://t.me/joinchat/AAAAAE8NqbV48l7ls-pFtQ)\n`{humanbytes(msg.file.size)}`"
        await event.client.send_message(
            entity=await event.client.get_entity(-1001326295477),
            file=msg.media,
            message=msj
        )
    else:
        await event.edit("`mesajı yanıtla`")


@bot.on(admin_cmd(pattern="sdown ?(.*)"))
async def _(event):
    if event.fwd_from:
        return
    d_link = event.pattern_match.group(1)
    if ".com" not in d_link:
        await event.edit("` I need a link to download something pro.`**(._.)**")
    else:
        msg = await event.edit("🎶**Müzik indirilip gönderiliyor..!**🎶")
        bot = "@spotify_to_mp3_bot"

        async with event.client.conversation(bot) as conv:
            try:
                await conv.send_message(d_link)
                details = await conv.get_response()
                for row in details.buttons:
                    for button in row:
                        if button.text == "📲🎵Download this Song!":
                            await button.click()
                            first = await conv.get_response()
                            if first.media:
                                msj = f"[{first.media.document.attributes[1].file_name}](https://t.me/joinchat/AAAAAE8NqbV48l7ls-pFtQ)\n`{humanbytes(first.media.document.size)}`"
                                await event.client.send_file(event.chat_id, first, caption=msj)
                                await msg.delete()
                            resp = await conv.get_response()
                            if resp.media:
                                msj = f"[{resp.media.document.attributes[1].file_name}](https://t.me/joinchat/AAAAAE8NqbV48l7ls-pFtQ)\n`{humanbytes(resp.media.document.size)}`"
                                await event.client.send_file(event.chat_id, resp, caption=msj)
                                await msg.delete()
            except YouBlockedUserError:
                await event.edit("**Error:** `unblock` @DeezLoadBot `and retry!`")
            except TimeoutError:
                return
