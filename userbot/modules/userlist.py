"""Get Administrators of any Chat*
Syntax: .userlist"""
import logging
import os

from telethon import events
from telethon.errors.rpcerrorlist import (ChatAdminRequiredError,
                                          MessageTooLongError)

from userbot import bot

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(events.NewMessage(pattern=r"\.userlists ?(.*)", outgoing=True))
async def get_users(show):
    """ For .userslist command, list all of the users of the chat. """
    if show.text[0].isalpha() or show.text[0] in ("/", "#", "@", "!"):
        return
    if not show.is_group:
        await show.edit("Are you sure this is a group?")
        return
    info = await show.client.get_entity(show.chat_id)
    title = info.title or "this chat"
    mentions = 'Users in {}: \n'.format(title)
    try:
        if show.pattern_match.group(1):
            searchq = show.pattern_match.group(1)
            async for user in show.client.iter_participants(show.chat_id, search=f'{searchq}'):
                if user.deleted:
                    mentions += f"\nDeleted Account `{user.id}`"
                else:
                    mentions += f"\n[{user.first_name}](tg://user?id={user.id}) `{user.id}`"
        else:
            async for user in show.client.iter_participants(show.chat_id):
                if user.deleted:
                    mentions += f"\nDeleted Account `{user.id}`"
                else:
                    mentions += f"\n[{user.first_name}](tg://user?id={user.id}) `{user.id}`"
    except ChatAdminRequiredError as err:
        mentions += " " + str(err) + "\n"
    try:
        await show.edit(mentions)
    except MessageTooLongError:
        await show.edit("Damn, this is a huge group. Uploading users lists as file.")
        with open("userslist.txt", "w+", encoding="utf-8") as file:
            file.write(mentions)
            file.close()
        await show.client.send_file(
            show.chat_id,
            "userslist.txt",
            caption='Users in {}'.format(title),
            reply_to=show.id,
        )
        os.remove("userslist.txt")
