# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot initialization. """


from mongoengine import connect
from sample_config import Config
from telemongo import MongoSession
from telethon import TelegramClient

connect('telegramsession', host=Config.MONGO_DB_URI)
session = MongoSession('telegramsession', host=Config.MONGO_DB_URI)

if session:
    bot = TelegramClient(session, Config.APP_ID, Config.API_HASH)
