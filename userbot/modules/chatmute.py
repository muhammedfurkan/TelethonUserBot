
from asyncio import sleep

from sample_config import Config
from userbot import bot
from userbot.util import admin_cmd, register


@bot.on(admin_cmd(pattern="unmutechat"))
async def unmute_chat(unm_e):
    """ For .unmutechat command, unmute a muted chat. """
    try:
        from sql_helpers.keep_read_sql import unkread
    except AttributeError:
        await unm_e.edit('`Running on Non-SQL Mode!`')
        return
    unkread(str(unm_e.chat_id))
    await unm_e.edit("```Unmuted this chat Successfully```")
    await sleep(2)
    await unm_e.delete()


@bot.on(admin_cmd(pattern="mutechat"))
async def mute_chat(mute_e):
    """ For .mutechat command, mute any chat. """
    try:
        from sql_helpers.keep_read_sql import kread
    except AttributeError:
        await mute_e.edit("`Running on Non-SQL mode!`")
        return
    await mute_e.edit(str(mute_e.chat_id))
    kread(str(mute_e.chat_id))
    await mute_e.edit("`Shush! This chat will be silenced!`")
    await sleep(2)
    await mute_e.delete()
    if Config.BOTLOG:
        await mute_e.client.send_message(
            Config.PRIVATE_GROUP_BOT_API_ID,
            str(mute_e.chat_id) + " was silenced.")


async def keep_read(message):
    """ The mute logic. """
    try:
        from sql_helpers.keep_read_sql import is_kread
    except AttributeError:
        return
    kread = is_kread()
    if kread:
        for i in kread:
            if i.groupid == str(message.chat_id):
                await message.client.send_read_acknowledge(message.chat_id)
