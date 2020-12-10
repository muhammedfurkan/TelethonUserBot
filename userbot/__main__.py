# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot start point """

import logging
import os
from importlib import import_module

from telethon.errors.rpcerrorlist import PhoneNumberInvalidError

from userbot import bot, tgbot
from userbot.modules import ALL_MODULES

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)

INVALID_PH = '\nERROR: The phone no. entered is incorrect' \
             '\n  Tip: Use country code (eg +44) along with num.' \
             '\n       Recheck your phone number'

try:
    bot.start()
    tgbot.start()
except PhoneNumberInvalidError:
    print(INVALID_PH)
    exit(1)

for module_name in ALL_MODULES:
    imported_module = import_module("userbot.modules." + module_name)
    load = "UserBot Modules Successfully Loaded: {}".format(module_name)

logger.info("Paperplane is alive! Test it by typing .alive on any chat."
            " Should you need assistance, head to https://t.me/tgpaperplane")

SEM_TEST = os.environ.get("SEMAPHORE", None)
if SEM_TEST:
    bot.disconnect()
else:
    bot.run_until_disconnected()
    tgbot.run_until_disconnected()
