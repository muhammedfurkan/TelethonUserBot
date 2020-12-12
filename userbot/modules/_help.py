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
import logging
import sys

from telethon import __version__, functions
from userbot import bot
from userbot.util import admin_cmd

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(admin_cmd(pattern="helpme ?(.*)", allow_sudo=True))
async def _(event):
    if event.fwd_from:
        return
    splugin_name = event.pattern_match.group(1)
    s_help_string = ""
    help_string = """
Python {}
Telethon {}
UserBot Forked from https://github.com/muhammedfurkan/TelethonUserBot""".format(
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
