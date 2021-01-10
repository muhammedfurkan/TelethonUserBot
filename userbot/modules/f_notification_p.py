from sample_config import Config
from telethon import custom, events
from telethon.tl.types import Channel
from telethon.utils import get_display_name
from userbot import bot, tgbot


@bot.on(events.NewMessage(incoming=True, blacklist_chats=Config.UB_BLACK_LIST_CHAT, func=lambda e: (e.mentioned)))
async def all_messages_catcher(event):
    # the bot might not have the required access_hash to mention the appropriate PM

    # construct message
    # the message format is stolen from @MasterTagAlertBot
    ammoca_message = ""

    who_ = await event.client.get_entity(event.sender_id)
    if (who_.bot or who_.verified or who_.support):
        return

    await (
        await event.forward_to(
            Config.TG_BOT_USER_NAME_BF_HER
        )
    ).delete()

    who_m = f"[{get_display_name(who_)}](tg://user?id={who_.id})"

    where_ = await event.client.get_entity(event.chat_id)

    where_m = get_display_name(where_)
    button_text = "📃 Mesaja git "

    if isinstance(where_, Channel):
        message_link = f"https://t.me/c/{where_.id}/{event.id}"
    else:
        # not an official link,
        # only works in DrKLO/Telegram,
        # for some reason
        message_link = f"tg://openmessage?chat_id={where_.id}&message_id={event.id}"
        # Telegram is weird :\

    ammoca_message += f"Etiketleyen: {who_m}\nGrup/Kişi:[{where_m}]({message_link}) "

    await tgbot.send_message(
        entity=Config.TAG_CHANNEL,
        message=ammoca_message,
        link_preview=False,
        buttons=[
            [custom.Button.url(button_text, message_link)]
        ],
        silent=True
    )
    e = await event.client.get_entity(Config.PM_LOGGR_BOT_API_ID)
    await event.client.forward_messages(e, event.message or event.media, silent=True)
