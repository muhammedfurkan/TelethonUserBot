# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot initialization. """

import os
from distutils.util import strtobool as sb
from logging import DEBUG, INFO, basicConfig, getLogger
from sys import version_info

from dotenv import load_dotenv
from telethon import TelegramClient,events
from telethon.sessions import StringSession

from sample_config import Config

if Config.HU_STRING_SESSION:
    bot = TelegramClient(StringSession(Config.HU_STRING_SESSION),Config.APP_ID,Config.API_HASH)
else:
    bot = TelegramClient("userbot", Config.APP_ID,Config.API_HASH)

if Config.TG_BOT_TOKEN_BF_HER:
    tgbot = TelegramClient("bot", Config.APP_ID,Config.API_HASH).start(bot_token=Config.TG_BOT_TOKEN_BF_HER)




# Global Variables
COUNT_MSG = 0
USERS = {}
COUNT_PM = {}
LASTMSG = {}
CMD_HELP = {}
AFKREASON = "no reason"
