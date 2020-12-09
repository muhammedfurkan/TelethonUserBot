from userbot.database.mongo import cli

cli = cli["Userbot"]["GBAN"]


async def get_gban():
    return cli.find()


async def add_chat_gban(chatid):
    if await is_gban(chatid) is True:
        print("FAILED")
        return False
    else:
        cli.insert_one({'chatid': chatid})


async def remove_chat_gban(chatid):
    if await is_gban(chatid) is False:
        return False
    cli.delete_one({'chatid': chatid})
    return True


async def is_gban(chatid):
    return bool(cli.find_one({"chatid": chatid}))
