"""**Know Your Unibot**
◇ list of all loaded plugins
◆ `.helpme`\n
◇ to know Data Center
◆ `.dc`\n
◇ powered by
◆ `.config`\n
◇ to know syntax
◆ `.syntax` <plugin name>
"""
import asyncio
import logging
import sys
from datetime import datetime

from telethon import __version__, functions
from userbot import bot
from userbot.util import admin_cmd

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)

DELETE_TIMEOUT = 5


@bot.on(admin_cmd(pattern="helpme ?(.*)", allow_sudo=True))
async def _(event):
    if event.fwd_from:
        return
    splugin_name = event.pattern_match.group(1)
    s_help_string = ""
    help_string = """
Python {}
Telethon {}
UserBot from https://github.com/muhammedfurkan/TelethonUserBot""".format(
        sys.version,
        __version__
    )

    await event.reply(help_string + "\n\n" + s_help_string, link_preview=False)

    await event.delete()


@bot.on(admin_cmd(pattern="dc"))
async def _(event):
    if event.fwd_from:
        return
    result = await bot(functions.help.GetNearestDcRequest())
    await event.edit(result.stringify())


@bot.on(admin_cmd(pattern="config"))
async def _(event):
    if event.fwd_from:
        return
    result = await bot(functions.help.GetConfigRequest())
    result = result.stringify()
    logger.info(result)
    await event.edit("""Telethon UserBot powered by @By_Azade""")


@bot.on(admin_cmd(pattern="send plugin (?P<shortname>\w+)$"))  # pylint:disable=E0602
async def send_plug_in(event):
    if event.fwd_from:
        return
    message_id = event.message.id
    input_str = event.pattern_match["shortname"]
    the_plugin_file = "./userbot/modules/{}.py".format(
        input_str)
    start = datetime.now()
    await bot.send_file(
        event.chat_id,
        the_plugin_file,
        force_document=True,
        allow_cache=False,
        reply_to=message_id
    )
    end = datetime.now()
    time_taken_in_ms = (end - start).seconds
    await event.edit("Uploaded {} in {} seconds".format(input_str, time_taken_in_ms))
    await asyncio.sleep(DELETE_TIMEOUT)
    await event.delete()
