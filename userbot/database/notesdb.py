from database.mongo import cli

cli = cli["Userbot"]['Notes']


async def get_notes(chatid):
    return cli.find({'chat_id': chatid})


async def get_note(chatid, name):
    return cli.find_one({'chat_id': chatid, 'name': name})


async def add_note(chatid, name, text):
    to_check = await get_note(chatid, name)

    if not to_check:
        cli.insert_one({'chat_id': chatid, 'name': name, 'text': text})

        return True
    else:
        cli.update_one(
            {
                '_id': to_check["_id"],
                'chat_id': to_check["chat_id"],
                'name': to_check["name"],
            }, {"$set": {
                'text': text
            }})

        return False


async def delete_note(chatid, name):
    to_check = await get_note(chatid, name)

    if not to_check:
        return False
    else:
        cli.delete_one({
            '_id': to_check["_id"],
            'chat_id': to_check["chat_id"],
            'name': to_check["name"],
            'text': to_check["text"],
        })
