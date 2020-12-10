from userbot.database.mongo import cli

cli = cli["Userbot"]["Filters"]


async def get_all_filters(chatid):
    return cli.find({'chat_id': chatid})


async def get_filter(chatid, keyword):
    return cli.find_one({'chat_id': chatid, 'keyword': keyword})


async def add_filter(chatid, keyword, msg_id):
    to_check = await get_filter(chatid, keyword)

    if not to_check:
        cli.insert_one({
            'chat_id': chatid,
            'keyword': keyword,
            'msg': msg_id
        })
        return True
    else:
        cli.update_one(
            {
                '_id': to_check["_id"],
                'chat_id': to_check["chat_id"],
                'keyword': to_check["keyword"],
            }, {"$set": {
                'msg': msg_id
            }})

        return False


async def delete_filter(chatid, keyword):
    to_check = await get_filter(chatid, keyword)

    if not to_check:
        return False
    cli.delete_one({
        '_id': to_check["_id"],
        'chat_id': to_check["chat_id"],
        'keyword': to_check["keyword"]
    })

    return True


async def delete_all_filters(chatid):
    return cli.delete_many({"chat_id": chatid})
