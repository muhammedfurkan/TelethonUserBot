"""Globally Ban users from all the
Group Administrations bots where you are SUDO
Available Commands:
.gban REASON
.ungban REASON"""
import logging

from sample_config import Config
from userbot import bot
from userbot.util import admin_cmd

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(admin_cmd(pattern="fban ?(.*)"))
async def _(event):
    if Config.G_BAN_LOGGER_GROUP is None:
        await event.edit("ENV VAR is not set. This module will not work.")
        return
    if event.fwd_from:
        return
    reason = event.pattern_match.group(1)
    if event.reply_to_msg_id:
        r = await event.get_reply_message()
        r_from_id = r.forward.sender_id or r.sender_id if r.forward else r.sender_id
        await event.client.send_message(
            Config.G_BAN_LOGGER_GROUP,
            "!fban {} {}".format(r_from_id, reason)
        )
    else:
        user_id = event.pattern_match.group(1)
        await event.client.send_message(
            Config.G_BAN_LOGGER_GROUP,
            "!fban {}".format(user_id)
        )
        async with event.client.conversation("PersonalBLBot") as conv:
            await conv.send_message("/edit")
            details = await conv.get_response()
            for row in details.buttons:
                for button in row:
                    if button.text == ("✍🏻 Edit Blacklist" and "✍🏻 Karalisteyi Düzenle" and "Banlananlar"):
                        await button.click()
                        await conv.send_message(user_id)
                        x = await conv.get_response()
                        for row in x.buttons:
                            for button in row:
                                if button.text == "✅ Tamamlandı":
                                    await button.click()
                                    break
        # await event.client.send_message(
        #     entity="PersonalBLBot",
        #     message="{}".format(user_id)
        # )
    await event.delete()


@bot.on(admin_cmd(pattern="unfban ?(.*)"))
async def _(event):
    if Config.G_BAN_LOGGER_GROUP is None:
        await event.edit("ENV VAR is not set. This module will not work.")
        return
    if event.fwd_from:
        return
    reason = event.pattern_match.group(1)
    if event.reply_to_msg_id:
        r = await event.get_reply_message()
        r_from_id = r.sender_id
        await event.client.send_message(
            Config.G_BAN_LOGGER_GROUP,
            "!unfban {} {}".format(r_from_id, reason)
        )
    else:
        user_id = event.pattern_match.group(1)
        await event.client.send_message(
            Config.G_BAN_LOGGER_GROUP,
            "!unfban {}".format(user_id)
        )
        async with event.client.conversation("PersonalBLBot") as conv:
            await conv.send_message("/edit")
            details = await conv.get_response()
            for row in details.buttons:
                for button in row:
                    if button.text == ("✍🏻 Edit Blacklist" and "✍🏻 Karalisteyi Düzenle" and "Banlananlar"):
                        await button.click()
                        await conv.send_message(f"/del {user_id}")
                        x = await conv.get_response()
                        for row in x.buttons:
                            for button in row:
                                if button.text == "✅ Tamamlandı":
                                    await button.click()
                                    break
    await event.delete()
