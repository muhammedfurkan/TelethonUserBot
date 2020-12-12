import logging

from userbot import bot
from userbot.util import admin_cmd

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(admin_cmd(pattern=("sil ?(.*)")))  # pylint:disable=E0602
async def _(event):
    await event.delete()
    chat = await event.get_chat()
    await event.client.delete_dialog(chat.id, revoke=True)
