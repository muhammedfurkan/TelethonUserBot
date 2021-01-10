""".promote\
\nUsage: Reply to someone's message with .promote to promote them.\
\n\n.demote\
\nUsage: Reply to someone's message with .demote to revoke their admin permissions.\
\n\n.ban\
\nUsage: Reply to someone's message with .ban to ban them.\
\n\n.unban\
\nUsage: Reply to someone's message with .unban to unban them in this chat.\
\n\n.mute\
\nUsage: Reply to someone's message with .mute to mute them, works on admins too.\
\n\n.unmute\
\nUsage: Reply to someone's message with .unmute to remove them from muted list.\
\n\n.gmute\
\nUsage: Reply to someone's message with .gmute to mute them in all groups you have in common with them.\
\n\n.ungmute\
\nUsage: Reply someone's message with .ungmute to remove them from the gmuted list.\
\n\n.delusers\
\nUsage: Searches for deleted accounts in a group. Use .delusers clean to remove deleted accounts from the group.\
\n\n.adminlist\
\nUsage: Retrieves all admins in a chat.\
\n\n.userslist or .userslist <name>\
\nUsage: Retrieves all users in a chat.
\n\n.undlt\
\nUsage: Sends the last deleted message in group."

Userbot module to help you manage a group.
"""

import asyncio
from asyncio import sleep
from os import remove

from sample_config import Config
from telethon import events
from telethon.errors import (BadRequestError, ChatAdminRequiredError,
                             ImageProcessFailedError, PhotoCropSizeSmallError,
                             UserAdminInvalidError)
from telethon.errors.rpcerrorlist import (MessageTooLongError,
                                          UserIdInvalidError)
from telethon.tl.functions.channels import (EditAdminRequest,
                                            EditBannedRequest,
                                            EditPhotoRequest)
from telethon.tl.functions.messages import UpdatePinnedMessageRequest
from telethon.tl.types import (ChannelParticipantsAdmins,
                               ChannelParticipantsBots, ChatAdminRights,
                               ChatBannedRights, MessageEntityMentionName,
                               MessageMediaPhoto, PeerChat)
from userbot import bot
from userbot.database.gmutedb import get_gmuted
from userbot.database.mutedb import get_muted
from userbot.database.servicemessagesdb import (add_chat_service,
                                                delete_service, get_service)
from userbot.util import admin_cmd

LOGGING_CHATID = Config.PRIVATE_GROUP_BOT_API_ID


ENABLE_LOG = True
LOGGING_CHATID = Config.PRIVATE_CHANNEL_BOT_API_ID
BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)
UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)
KICK_RIGHTS = ChatBannedRights(until_date=None, view_messages=True)
MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)
UNMUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)


@bot.on(admin_cmd(pattern="servicemessage ?(.*)"))
async def serv_msg(event):
    text = event.pattern_match.group(1)
    if text == "on":
        chat = await event.get_chat()
        admin = chat.admin_rights
        creator = chat.creator
        check = await get_service(event.chat_id)
        if not admin and not creator:
            await event.edit("`I am not an admin!`")
            return

        await add_chat_service(event.chat_id)
        await event.edit("`Anti-Service messages deletion activated`")


@bot.on(admin_cmd(pattern="servicemessage ?(.*)"))
async def serv_msg(event):
    text = event.pattern_match.group(1)
    if text == "off":
        chat = await event.get_chat()
        admin = chat.admin_rights
        creator = chat.creator
        check = await get_service(event.chat_id)
        if not admin and not creator:
            await event.edit("`I am not an admin!`")
            return
        if check['chatid'] == event.chat_id:
            await delete_service(event.chat_id)
            await event.edit("`Anti-Service messages deletion disabled`")


@bot.on(events.ChatAction())
async def delete_service_msg(event):
    try:
        chat = await event.get_chat()
        admin = chat.admin_rights
        creator = chat.creator
        check = await get_service(event.chat_id)
        if not admin and not creator:
            return
        else:
            if check['chatid'] == event.chat_id:
                await event.delete()
    except TypeError:
        pass


@bot.on(events.NewMessage(outgoing=True, pattern="^.setgic$"))
async def setgrouppic(eventPic):
    if eventPic.text[0].isalpha() or eventPic.text[0] in ("/", "#", "@", "!"):
        return
    if eventPic.reply_to_msg_id:
        replymsg = await eventPic.get_reply_message()
        chat = await eventPic.get_chat()
        admin = chat.admin_rights
        creator = chat.creator
        photo = None
        if not admin and not creator:
            await eventPic.edit("`I am not an admin!`")
            return
        if replymsg and replymsg.media:
            if isinstance(replymsg.media, MessageMediaPhoto):
                photo = await eventPic.client.download_media(message=replymsg.photo)
            elif "image" in replymsg.media.document.mime_type.split("/"):
                photo = await eventPic.client.download_file(replymsg.media.document)
            else:
                await eventPic.edit("`Invalid Extension`")
        if photo:
            try:
                await eventPic.client(
                    EditPhotoRequest(
                        eventPic.chat_id, await eventPic.client.upload_file(photo)
                    )
                )
                await eventPic.edit("`Chat Picture Changed`")

            except PhotoCropSizeSmallError:
                await eventPic.edit("`The image is too small`")
            except ImageProcessFailedError:
                await eventPic.edit("`Failure while processing the image`")
    else:
        await eventPic.edit(
            "`Reply .setgrouppic to an Image to set it as group's icon.`"
        )


@bot.on(events.NewMessage(outgoing=True, pattern="^.promote(?: |$)(.*)"))
async def promote(eventPromote):
    if eventPromote.text[0].isalpha() or eventPromote.text[0] in (
        "/",
        "#",
        "@",
        "!",
    ):
        return
    chat = await eventPromote.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await eventPromote.edit("`I am not an admin!`")
        return
    newAdminRights = ChatAdminRights(
        add_admins=False,
        invite_users=True,
        change_info=False,
        ban_users=True,
        delete_messages=True,
        pin_messages=True,
    )
    await eventPromote.edit("`Bu kişiyi yetkilendiriyorum...`")
    user = await get_user_from_event(eventPromote)
    if not user:
        return
    try:
        await eventPromote.client(
            EditAdminRequest(eventPromote.chat_id, user.id,
                             newAdminRights, rank="")
        )
        await eventPromote.edit("`Başarıyla yetkilendirildi!`")
    except BadRequestError:
        await eventPromote.edit("`Yeterli yetkilerim yok!`")
        return
    if ENABLE_LOG:
        await eventPromote.client.send_message(
            LOGGING_CHATID,
            "#PROMOTE\n"
            f"USER: [{user.first_name}](tg://user?id={user.id})\n"
            f"CHAT: {eventPromote.chat.title}(`{eventPromote.chat_id}`)",
        )


@bot.on(events.NewMessage(outgoing=True, pattern="^.demote(?: |$)(.*)"))
async def demote(eventDemote):
    if eventDemote.text[0].isalpha() or eventDemote.text[0] in (
        "/",
        "#",
        "@",
        "!",
    ):
        return
    chat = await eventDemote.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await eventDemote.edit("`I am not an admin!`")
        return
    await eventDemote.edit("`Demoting...`")
    user = await get_user_from_event(eventDemote)
    if not user:
        return
    newAdminRights = ChatAdminRights(
        add_admins=None,
        invite_users=None,
        change_info=None,
        ban_users=None,
        delete_messages=None,
        pin_messages=None,
    )
    try:
        await eventDemote.client(
            EditAdminRequest(eventDemote.chat_id, user.id,
                             newAdminRights, rank="")
        )
    except BadRequestError:
        await eventDemote.edit("`I don't have sufficient permissions!`")
        return
    await eventDemote.edit("`Yetkileri başarıyla kaldırıldı!`")
    if ENABLE_LOG:
        await eventDemote.client.send_message(
            LOGGING_CHATID,
            "#DEMOTE\n"
            f"USER: [{user.first_name}](tg://user?id={user.id})\n"
            f"CHAT: {eventDemote.chat.title}(`{eventDemote.chat_id}`)",
        )


@bot.on(events.NewMessage(outgoing=True, pattern="^.ban(?: |$)(.*)"))
async def ban(eventBan):
    if eventBan.text[0].isalpha() or eventBan.text[0] in ("/", "#", "@", "!"):
        return
    chat = await eventBan.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await eventBan.edit("`I am not an admin!`")
        return
    user = await get_user_from_event(eventBan)
    if not user:
        return
    await eventBan.edit("`Banlanacak kişiyi arıyorum...`")
    try:
        await eventBan.client(
            EditBannedRequest(eventBan.chat_id, user.id, BANNED_RIGHTS)
        )
    except BadRequestError:
        await eventBan.edit("`I don't have sufficient permissions!`")
        return
    try:
        reply = await eventBan.get_reply_message()
        if reply:
            await reply.delete()
    except BadRequestError:
        await eventBan.edit(
            "`I dont have message nuking rights! But still he was banned!`"
        )
        return
    await eventBan.edit(f"[{user.first_name}](tg://user?id={user.id}) banlandı!")
    if ENABLE_LOG:
        await eventBan.client.send_message(
            LOGGING_CHATID,
            "#BAN\n"
            f"USER: [{user.first_name}](tg://user?id={user.id})\n"
            f"CHAT: {eventBan.chat.title}(`{eventBan.chat_id}`)",
        )


@bot.on(events.NewMessage(outgoing=True, pattern="^.bots$"))
async def listbots(eventListBots):
    info = await eventListBots.client.get_entity(eventListBots.chat_id)
    title = info.title or "this chat"
    mentions = f"<b>Bots in {title}:</b>\n"
    try:
        if isinstance(eventListBots.to_id, PeerChat):
            await eventListBots.edit("`Only Supergroups can have bots.`")
            return
        else:
            async for user in eventListBots.client.iter_participants(
                eventListBots.chat_id, filter=ChannelParticipantsBots
            ):
                if not user.deleted:
                    link = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
                    userid = f"<code>{user.id}</code>"
                    mentions += f"\n{link} {userid}"
                else:
                    mentions += f"\n<code>{user.id}</code>(Bot deleted by owner)"
    except ChatAdminRequiredError as err:
        mentions += " " + str(err) + "\n"
    try:
        await eventListBots.edit(mentions, parse_mode="html")
    except MessageTooLongError:
        await eventListBots.edit(
            "This group is filled with bots as hell. Uploading bots list as file."
        )
        with open("botlist.txt", "w") as file:
            file.write(mentions)
            file.close()
        # file = open("botlist.txt", "w+")
        # file.write(mentions)
        # file.close()
        await eventListBots.client.send_file(
            eventListBots.chat_id,
            "botlist.txt",
            caption="Bots in {}".format(title),
            reply_to=eventListBots.id,
        )
        remove("botlist.txt")


@bot.on(events.NewMessage(outgoing=True, pattern="^.unban(?: |$)(.*)"))
async def unban(eventUnban):
    if eventUnban.text[0].isalpha() or eventUnban.text[0] in (
        "/",
        "#",
        "@",
        "!",
    ):
        return
    chat = await eventUnban.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await eventUnban.edit("`I am not an admin!`")
        return
    await eventUnban.edit("Unbanning!`")
    user = await get_user_from_event(eventUnban)
    if not user:
        return
    try:
        await eventUnban.client(
            EditBannedRequest(eventUnban.chat_id, user.id, UNBAN_RIGHTS)
        )
        await eventUnban.edit("```Unbanned Successfully```")
        if ENABLE_LOG:
            await eventUnban.client.send_message(
                LOGGING_CHATID,
                "#UNBAN\n"
                f"USER: [{user.first_name}](tg://user?id={user.id})\n"
                f"CHAT: {eventUnban.chat.title}(`{eventUnban.chat_id}`)",
            )
    except UserIdInvalidError:
        await eventUnban.edit("`Uh oh my unban logic broke!`")


@bot.on(events.NewMessage(outgoing=True, pattern="^.mutechat$"))
async def mute_chat(mute_e):
    from userbot.database.mongo import cli
    cli = cli["Userbot"]["mute_chat"]
    """ For .mutechat command, mute any chat. """
    await mute_e.edit(str(mute_e.chat_id))
    cli.insert_one({"chat_id": mute_e.chat_id})
    user = await get_user_from_id(mute_e.sender_id, mute_e)
    await mute_e.edit("`Shush! This chat will be silenced!`")
    if ENABLE_LOG:
        await mute_e.client.send_message(
            LOGGING_CHATID,
            "#CHAT_MUTE\n"
            f"USER: [{user.first_name}](tg://user?id={user.id})\n"
            f"CHAT: {mute_e.chat.title}(`{mute_e.chat_id}`)",
        )


@bot.on(events.NewMessage(outgoing=True, pattern="^.unmutechat$"))
async def unmute_chat(unm_e):
    """ For .unmutechat command, unmute a muted chat. """
    from userbot.database.mongo import cli
    cli = cli["Userbot"]["mute_chat"]
    cli.delete_one({"chat_id": unm_e.chat_id})
    await unm_e.edit("```Unmuted this chat Successfully```")


@bot.on(events.NewMessage(incoming=True))
async def keep_read(message):
    """ The mute logic. """
    from userbot.database.mongo import cli
    cli = cli["Userbot"]["mute_chat"]
    kread = cli.find({"chat_id": message.chat_id})
    if kread:
        for i in kread:
            if i["chat_id"] == message.chat_id:
                await message.client.send_read_acknowledge(
                    entity=message.chat_id,
                    max_id=0,
                    clear_mentions=True
                )


@bot.on(events.NewMessage(outgoing=True, pattern="^.mute(?: |$)(.*)"))
async def mute(eventMute):
    if eventMute.text[0].isalpha() or eventMute.text[0] in (
        "/",
        "#",
        "@",
        "!",
    ):
        return
    try:
        from userbot.database.mutedb import mute
    except AttributeError:
        await eventMute.edit("`Running on Non-SQL mode!`")
        return
    chat = await eventMute.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await eventMute.edit("`I am not an admin!`")
        return

    user = await get_user_from_event(eventMute)
    if not user:
        return
    self_user = await eventMute.client.get_me()
    if user.id == self_user.id:
        await eventMute.edit("`Hands too short, can't duct tape myself...\n(ヘ･_･)ヘ┳━┳`")
        return
    await eventMute.edit("`Gets a tape!`")
    if await mute(eventMute.chat_id, user.id) is False:
        return await eventMute.edit("`Error! User probably already muted.`")
    else:
        try:
            await eventMute.client(
                EditBannedRequest(eventMute.chat_id, user.id, MUTE_RIGHTS)
            )
            await eventMute.edit("`Safely taped!`")
            if ENABLE_LOG:
                await eventMute.client.send_message(
                    LOGGING_CHATID,
                    "#MUTE\n"
                    f"USER: [{user.first_name}](tg://user?id={user.id})\n"
                    f"CHAT: {eventMute.chat.title}(`{eventMute.chat_id}`)",
                )
        except UserIdInvalidError:
            return await eventMute.edit("`Uh oh my mute logic broke!`")


@bot.on(events.NewMessage(outgoing=True, pattern="^.unmute(?: |$)(.*)"))
async def unmute(eventUnMute):
    if eventUnMute.text[0].isalpha() or eventUnMute.text[0] in (
        "/",
        "#",
        "@",
        "!",
    ):
        return
    chat = await eventUnMute.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await eventUnMute.edit("`I am not an admin!`")
        return
    try:
        from userbot.database.mutedb import unmute
    except AttributeError:
        await eventUnMute.edit("`Running on Non-SQL mode!`")
        return
    await eventUnMute.edit("```Unmuting...```")
    user = await get_user_from_event(eventUnMute)
    if not user:
        return
    if await unmute(eventUnMute.chat_id, user.id) is False:
        return await eventUnMute.edit("`Error! User probably already unmuted.`")
    try:
        await eventUnMute.client(
            EditBannedRequest(eventUnMute.chat_id, user.id, UNBAN_RIGHTS)
        )
        await eventUnMute.edit("```Unmuted Successfully```")
    except UserIdInvalidError:
        await eventUnMute.edit("`Uh oh my unmute logic broke!`")
        return

    if ENABLE_LOG:
        await eventUnMute.client.send_message(
            LOGGING_CHATID,
            "#UNMUTE\n"
            f"USER: [{user.first_name}](tg://user?id={user.id})\n"
            f"CHAT: {eventUnMute.chat.title}(`{eventUnMute.chat_id}`)",
        )


@bot.on(events.NewMessage(incoming=True))
async def muter(mutedMessage):
    try:
        pass
    except AttributeError:
        return
    muted = await get_muted(mutedMessage.chat_id)
    gmuted = await get_gmuted()
    rights = ChatBannedRights(
        until_date=None,
        send_messages=True,
        send_media=True,
        send_stickers=True,
        send_gifs=True,
        send_games=True,
        send_inline=True,
        embed_links=True,
    )
    if muted:
        for i in muted:
            if i['chat_id'] == mutedMessage.sender_id:
                await mutedMessage.delete()
                try:
                    await mutedMessage.client(
                        EditBannedRequest(mutedMessage.chat_id,
                                          mutedMessage.sender_id, rights)
                    )
                except (UserAdminInvalidError, ChatAdminRequiredError, BadRequestError, UserIdInvalidError):
                    pass
    for i in gmuted:
        if i['chat_id'] == mutedMessage.sender_id:
            await mutedMessage.delete()


@bot.on(events.NewMessage(outgoing=True, pattern="^.gmute(?: |$)(.*)"))
async def gmute(eventGmute):
    if eventGmute.text[0].isalpha() or eventGmute.text[0] in (
        "/",
        "#",
        "@",
        "!",
    ):
        return
    chat = await eventGmute.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await eventGmute.edit("`I am not an admin!`")
        return
    try:
        from userbot.database.gmutedb import gmute
    except AttributeError:
        await eventGmute.edit("`Running on Non-SQL mode!`")
        return

    user = await get_user_from_event(eventGmute)
    if not user:
        return
    await eventGmute.edit("`Grabs a huge, sticky duct tape!`")
    if await gmute(user.id) is False:
        await eventGmute.edit(
            "`Error! User probably already gmuted.`"
        )
    else:
        await eventGmute.edit("`Haha Yash! Globally taped!`")

        if ENABLE_LOG:
            await eventGmute.client.send_message(
                LOGGING_CHATID,
                "#GMUTE\n"
                f"USER: [{user.first_name}](tg://user?id={user.id})\n"
                f"CHAT: {eventGmute.chat.title}(`{eventGmute.chat_id}`)",
            )


@bot.on(events.NewMessage(outgoing=True, pattern="^.ungmute(?: |$)(.*)"))
async def ungmute_(eventUnGmute):
    if eventUnGmute.text[0].isalpha() or eventUnGmute.text[0] in (
        "/",
        "#",
        "@",
        "!",
    ):
        return
    chat = await eventUnGmute.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await eventUnGmute.edit("`I am not an admin!`")
        return
    try:
        from userbot.database.gmutedb import ungmute
    except AttributeError:
        await eventUnGmute.edit("`Running on Non-SQL mode!`")
        return
    user = await get_user_from_event(eventUnGmute)
    if not user:
        return
    await eventUnGmute.edit("```Ungmuting...```")

    if await ungmute(user.id) is False:
        await eventUnGmute.edit("`Error! User probably not gmuted.`")
    else:
        await eventUnGmute.edit("```Ungmuted Successfully```")

        if ENABLE_LOG:
            await eventUnGmute.client.send_message(
                LOGGING_CHATID,
                "#UNGMUTE\n"
                f"USER: [{user.first_name}](tg://user?id={user.id})\n"
                f"CHAT: {eventUnGmute.chat.title}(`{eventUnGmute.chat_id}`)",
            )


@bot.on(events.NewMessage(outgoing=True, pattern="^.delusers(?: |$)(.*)"))
async def rm_deletedacc(eventDeletedAccs):
    if eventDeletedAccs.text[0].isalpha() or eventDeletedAccs.text[0] in (
        "/",
        "#",
        "@",
        "!",
    ):
        return

    con = eventDeletedAccs.pattern_match.group(1)
    del_u = 0
    del_status = "`No deleted accounts found, Group is cleaned as Hell`"

    if not eventDeletedAccs.is_group:
        await eventDeletedAccs.edit("`This command is only for groups!`")
        return
    if con != "clean":
        await eventDeletedAccs.edit("`Searching for ded af accounts...`")
        async for user in eventDeletedAccs.client.iter_participants(
            eventDeletedAccs.chat_id
        ):
            if user.deleted:
                del_u += 1

        if del_u > 0:
            del_status = f"found **{del_u}** deleted account(s) in this group \
                \nClean them by using .delusers clean"
        await eventDeletedAccs.edit(del_status)
        return
    chat = await eventDeletedAccs.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await eventDeletedAccs.edit("`I am not an admin here!`")
        return
    await eventDeletedAccs.edit("`Deleting deleted accounts...\nOh I can do that?!?!`")
    del_u = 0
    del_a = 0
    async for user in eventDeletedAccs.client.iter_participants(
        eventDeletedAccs.chat_id
    ):
        if user.deleted:
            try:
                await eventDeletedAccs.client(
                    EditBannedRequest(eventDeletedAccs.chat_id,
                                      user.id, BANNED_RIGHTS)
                )
            except ChatAdminRequiredError:
                await eventDeletedAccs.edit("`I don't have ban rights in this group`")
                return
            except UserAdminInvalidError:
                del_u -= 1
                del_a += 1
            await eventDeletedAccs.client(
                EditBannedRequest(eventDeletedAccs.chat_id,
                                  user.id, UNBAN_RIGHTS)
            )
            del_u += 1
    if del_u > 0:
        del_status = f"Cleaned **{del_u}** deleted account(s)"
    if del_a > 0:
        del_status = f"Cleaned **{del_u}** deleted account(s) \
            \n**{del_a}** deleted admin accounts are not removed."
    await eventDeletedAccs.edit(del_status)


@bot.on(events.NewMessage(outgoing=True, pattern="^.adminlist$"))
async def listadmins(eventListAdmins):
    if eventListAdmins.text[0].isalpha() or eventListAdmins.text[0] in (
        "/",
        "#",
        "@",
        "!",
    ):
        return

    if not eventListAdmins.is_group:
        await eventListAdmins.edit("I don't think this is a group.")
        return
    info = await eventListAdmins.client.get_entity(eventListAdmins.chat_id)
    title = info.title or "this chat"
    mentions = f"<b>Admins in {title}:</b> \n"
    try:
        async for user in eventListAdmins.client.iter_participants(
            eventListAdmins.chat_id, filter=ChannelParticipantsAdmins
        ):
            if not user.deleted:
                link = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
                userid = f"<code>{user.id}</code>"
                mentions += f"\n{link} {userid}"
            else:
                mentions += f"\nDeleted Account <code>{user.id}</code>"
    except ChatAdminRequiredError as err:
        mentions += " " + str(err) + "\n"
    await eventListAdmins.edit(mentions, parse_mode="html")


@bot.on(events.NewMessage(outgoing=True, pattern="^.pin(?: |$)(.*)"))
async def pinmessage(eventPinMessage):
    if eventPinMessage.text[0].isalpha() or eventPinMessage.text[0] in (
        "/",
        "#",
        "@",
        "!",
    ):
        return
    chat = await eventPinMessage.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await eventPinMessage.edit("`I am not an admin!`")
        return
    to_pin = eventPinMessage.reply_to_msg_id
    if not to_pin:
        await eventPinMessage.edit("`Reply to a message to pin it.`")
        return
    options = eventPinMessage.pattern_match.group(1)
    is_silent = True
    if options.lower() == "loud":
        is_silent = False
    try:
        await eventPinMessage.client(
            UpdatePinnedMessageRequest(
                eventPinMessage.to_id, to_pin, is_silent)
        )
    except BadRequestError:
        await eventPinMessage.edit("`I don't have sufficient permissions!`")
        return
    await eventPinMessage.edit("`Pinned Successfully!`")
    user = await get_user_from_id(eventPinMessage.sender_id, eventPinMessage)
    if ENABLE_LOG:
        await eventPinMessage.client.send_message(
            LOGGING_CHATID,
            "#PIN\n"
            f"ADMIN: [{user.first_name}](tg://user?id={user.id})\n"
            f"CHAT: {eventPinMessage.chat.title}(`{eventPinMessage.chat_id}`)\n"
            f"LOUD: {not is_silent}",
        )


@bot.on(events.NewMessage(outgoing=True, pattern="^.kick(?: |$)(.*)"))
async def kick(eventKickUser):
    if eventKickUser.text[0].isalpha() or eventKickUser.text[0] in (
        "/",
        "#",
        "@",
        "!",
    ):
        return
    chat = await eventKickUser.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await eventKickUser.edit("`I am not an admin!`")
        return
    user = await get_user_from_event(eventKickUser)
    if not user:
        await eventKickUser.edit("`Couldn't fetch user.`")
        return
    await eventKickUser.edit("`Kicking this users...`")
    try:
        await eventKickUser.client(
            EditBannedRequest(eventKickUser.chat_id, user.id, KICK_RIGHTS)
        )
        await sleep(0.5)
    except BadRequestError:
        await eventKickUser.edit("`I don't have sufficient permissions!`")
        return
    await eventKickUser.client(
        EditBannedRequest(
            eventKickUser.chat_id, user.id, ChatBannedRights(until_date=None)
        )
    )
    await eventKickUser.edit(
        f"[{user.first_name}](tg://user?id={user.id})` `atıldı` !`"
    )
    if ENABLE_LOG:
        await eventKickUser.client.send_message(
            LOGGING_CHATID,
            "#KICK\n"
            f"USER: [{user.first_name}](tg://user?id={user.id})\n"
            f"CHAT: {eventKickUser.chat.title}(`{eventKickUser.chat_id}`)\n",
        )


@bot.on(events.NewMessage(outgoing=True, pattern="^.userslist ?(.*)"))
async def list_users(eventListUsers):
    if eventListUsers.text[0].isalpha() or eventListUsers.text[0] in (
        "/",
        "#",
        "@",
        "!",
    ):
        return
    if not eventListUsers.is_group:
        await eventListUsers.edit("Are you sure this is a group?")
        return
    info = await eventListUsers.client.get_entity(eventListUsers.chat_id)
    title = info.title or "this chat"
    mentions = "Users in {}: \n".format(title)
    try:
        if eventListUsers.pattern_match.group(1):
            searchq = eventListUsers.pattern_match.group(1)
            async for user in eventListUsers.client.iter_participants(
                eventListUsers.chat_id, search=f"{searchq}"
            ):
                if user.deleted:
                    mentions += f"\nDeleted Account `{user.id}`"
                else:
                    mentions += (
                        f"\n[{user.first_name}](tg://user?id={user.id}) `{user.id}`"
                    )
        else:
            async for user in eventListUsers.client.iter_participants(
                eventListUsers.chat_id
            ):
                if user.deleted:
                    mentions += f"\nDeleted Account `{user.id}`"
                else:
                    mentions += (
                        f"\n[{user.first_name}](tg://user?id={user.id}) `{user.id}`"
                    )
    except ChatAdminRequiredError as err:
        mentions += " " + str(err) + "\n"
    try:
        await eventListUsers.edit(mentions)
    except MessageTooLongError:
        await eventListUsers.edit(
            "Damn, this is a huge group. Uploading users lists as file."
        )
        with open("userslist.txt", "w+", encoding="utf-8") as file:
            file.write(mentions)
            file.close()
        await eventListUsers.client.send_file(
            eventListUsers.chat_id,
            "userslist.txt",
            caption="Users in {}".format(title),
            reply_to=eventListUsers.id,
        )
        remove("userslist.txt")


@bot.on(admin_cmd(pattern="undlt ?(.*)"))
async def _(event):
    if event.fwd_from:
        return
    c = await event.get_chat()
    file_ = event.pattern_match.group(1)
    if c.admin_rights or c.creator:
        if file_ == "media":
            await event.edit("`silinmiş medya getiriliyor`")
            async for j in event.client.iter_admin_log(event.chat_id, delete=True):
                if j.old.media is not None:
                    x = await event.client.download_media(j.old.media)
                    await event.client.send_message(entity=event.chat_id, file=x)
        else:
            a = await bot.get_admin_log(
                event.chat_id, limit=10, edit=False, delete=True
            )
            deleted_msg = "Deleted message in this group:"
            for i in a:
                if i.old.message != "":
                    deleted_msg += "\n👉`{}`".format(i.old.message)
                    await event.edit(deleted_msg)
    else:
        await event.edit(
            "`You need administrative permissions in order to do this command`"
        )
        await asyncio.sleep(3)
        await event.delete()


async def get_user_from_event(event):
    """ Get the user from argument or replied message. """
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        user_obj = await event.client.get_entity(previous_message.from_id)
    else:
        user = event.pattern_match.group(1)

        if user.isnumeric():
            user = int(user)

        if not user:
            await event.edit("`Pass the user's username, id or reply!`")
            return

        if event.message.entities is not None:
            probable_user_mention_entity = event.message.entities[0]

            if isinstance(probable_user_mention_entity,
                          MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                user_obj = await event.client.get_entity(user_id)
                return user_obj
        try:
            user_obj = await event.client.get_entity(user)
        except (TypeError, ValueError) as err:
            await event.edit(str(err))
            return None

    return user_obj


async def get_user_from_id(user, event):
    """ Getting user from user ID """
    if isinstance(user, str):
        user = int(user)

    try:
        user_obj = await event.client.get_entity(user)
    except (TypeError, ValueError) as err:
        await event.edit(str(err))
        return None

    return user_obj
