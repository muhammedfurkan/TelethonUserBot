from userbot.database.mongo import cli

cli = cli["Userbot"]["Gmute"]


async def gmute(userid):
    if await is_gmuted(userid) is True:
        return False
    cli.insert_one({'user_id': userid})
    return True


async def is_gmuted(userid):
    is_gmuted = cli.find_one({'user_id': userid})

    return bool(is_gmuted)


async def ungmute(userid):
    if await is_gmuted(userid) is False:
        return False
    cli.delete_one({'user_id': userid})
    return True


async def get_gmuted():
    gmuted_db = cli.find()
    return [user["user_id"] for user in gmuted_db]
