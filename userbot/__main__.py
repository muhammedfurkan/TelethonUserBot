# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot start point """

import glob
import logging
import os
from pathlib import Path

from sample_config import Config
from telethon.errors.rpcerrorlist import PhoneNumberInvalidError

from userbot import bot, tgbot
from userbot.util import load_module, remove_plugin

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

NO_LOAD = Config.NO_LOAD
path = 'userbot/modules/*.py'
files = glob.glob(path)
for name in files:
    with open(name) as f:
        path1 = Path(f.name)
        shortname = path1.stem
        load_module(shortname.replace(".py", ""))
for noload in NO_LOAD:
    remove_plugin(noload)
    print(f"Removed plugin {noload}")


SEM_TEST = os.environ.get("SEMAPHORE", None)
if SEM_TEST:
    bot.disconnect()
else:
    bot.run_until_disconnected()
    tgbot.run_until_disconnected()
