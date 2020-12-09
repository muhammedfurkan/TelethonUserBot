from userbot.database.mongo import cli

cli = cli["Userbot"]["Mute"]


# Mutes
async def mute(chatid, userid):
    if await is_muted(chatid, userid) is True:
        return False
    cli.insert_one({'chat_id': chatid, 'user_id': userid})
    return True


async def is_muted(chatid, userid):
    is_muted = cli.find_one({'chat_id': chatid, 'user_id': userid})

    return bool(is_muted)


async def unmute(chatid, userid):
    if await is_muted(chatid, userid) is False:
        return False
    cli.delete_one({'chat_id': chatid, 'user_id': userid})
    return True


async def get_muted(chatid):
    muted_db = cli.find({'chat_id': int(chatid)})

    return [user["user_id"] for user in muted_db]
