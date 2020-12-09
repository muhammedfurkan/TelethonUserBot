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

from sample_config import Config
from userbot import bot
from userbot.util import admin_cmd, register

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(admin_cmd(pattern="helpme ?(.*)", allow_sudo=True))
async def _(event):
    if event.fwd_from:
        return
    splugin_name = event.pattern_match.group(1)
    if splugin_name in bot._plugins:
        s_help_string = bot._plugins[splugin_name].__doc__
    else:
        s_help_string = ""
    help_string = """@Unibot
Python {}
Telethon {}
UserBot Forked from https://github.com/muhammedfurkan/unibot""".format(
        sys.version,
        __version__
    )
    tgbotusername = Config.TG_BOT_USER_NAME_BF_HER
    if tgbotusername is not None:
        results = await bot.inline_query(
            tgbotusername,
            help_string + "\n\n" + s_help_string
        )
        await results[0].click(
            event.chat_id,
            reply_to=event.reply_to_msg_id,
            hide_via=True
        )
    else:
        await event.reply(help_string + "\n\n" + s_help_string)

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
    await event.edit("""Telethon UserBot powered by @Unibot""")


@bot.on(admin_cmd(pattern="syntax (.*)"))
async def _(event):
    if event.fwd_from:
        return
    plugin_name = event.pattern_match.group(1)
    if plugin_name in bot._plugins:
        help_string = bot._plugins[plugin_name].__doc__
        unload_string = f"Use `.unload {plugin_name}` to remove this plugin.\n           © @Unibot"
        if help_string:
            plugin_syntax = f"Syntax for plugin **{plugin_name}**:\n\n{help_string}\n{unload_string}"
        else:
            plugin_syntax = f"No DOCSTRING has been setup for {plugin_name} plugin."
    else:
        plugin_syntax = "Enter valid **Plugin** name.\nDo `.exec ls stdplugins` or `.helpme` to get list of valid plugin names."
    await event.edit(plugin_syntax)
