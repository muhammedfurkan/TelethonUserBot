from userbot.database.mongo import cli

cli = cli["Userbot"]["Fban"]


async def get_fban():
    return cli.find()


async def add_chat_fban(chatid):
    if await is_fban(chatid) is True:
        return False
    else:
        cli.insert_one({'chatid': chatid})


async def remove_chat_fban(chatid):
    if await is_fban(chatid) is False:
        return False
    cli.delete_one({'chatid': chatid})
    return True


async def is_fban(chatid):
    if cli.find_one({"chatid": chatid}):
        return True

    print("FAILED on fed")
    return False
