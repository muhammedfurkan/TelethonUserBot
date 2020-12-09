# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Urban Dictionary
Syntax: .ud Query"""
import logging

import urbandict

from userbot import bot
from userbot.util import admin_cmd, register

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(admin_cmd(pattern="ud (.*)"))
async def _(event):
    if event.fwd_from:
        return
    await event.edit("processing...")
    str = event.pattern_match.group(1)
    try:
        mean = urbandict.define(str)
        if len(mean) > 0:
            await event.edit(
                'Text: **' +
                str +
                '**\n\nMeaning: **' +
                mean[0]['def'] +
                '**\n\n' +
                'Example: \n__' +
                mean[0]['example'] +
                '__'
            )
        else:
            await event.edit("No result found for **" + str + "**")
    except:
        await event.edit("No result found for **" + str + "**")
