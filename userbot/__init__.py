
from sample_config import Config
from telethon import TelegramClient
from telethon.sessions import StringSession

if Config.HU_STRING_SESSION:
    bot = TelegramClient(StringSession(
        Config.HU_STRING_SESSION), Config.APP_ID, Config.API_HASH)
else:
    bot = TelegramClient("telethonuserbot", Config.APP_ID, Config.API_HASH)

if Config.TG_BOT_TOKEN_BF_HER:
    tgbot = TelegramClient("bot", Config.APP_ID, Config.API_HASH).start(
        bot_token=Config.TG_BOT_TOKEN_BF_HER)
