from userbot.database.mongo import cli

cli = cli["Userbot"]["servicemsg"]


async def get_service(chatid):
    return cli.find_one({'chatid': chatid})


async def add_chat_service(chatid):
    check = await get_service(chatid)

    if not check:
        cli.insert_one(
            {
                'chatid': chatid
            }
        )
        return True
    else:
        cli.update_one(
            {
                '_id': check['id'],
            },
            {'&set': {
                'chatid': check['chatid']
            }}
        )
        return False


async def delete_service(chatid):
    to_check = await get_service(chatid)

    if not to_check:
        return False
    cli.delete_one({
        '_id': to_check["_id"],
        'chatid': to_check["chatid"]
    })

    return True
