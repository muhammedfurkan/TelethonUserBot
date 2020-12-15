from userbot.database.mongo import cli

cli = cli["Userbot"]["lydia"]


async def is_chat(chat_id):
    return cli.find_one({'chat_id': chat_id})


async def list_chat():
    return cli.find({})


async def set_ses(chat_id, ses_id, expires):
    check = await is_chat(chat_id)
    if not check:
        cli.insert_one(
            {
                'chat_id': chat_id,
                'ses_id': ses_id,
                'expires': expires
            }
        )
        return True
    else:
        cli.update_one(
            {
                '_id': check['_id'],
            }, {'$set': {
                'ses_id': check['ses_id'],
                'expires': check['expires']
            }}
        )
        return False


async def get_ses(chat_id):
    check = await is_chat(chat_id)
    if check:
        sesh = check['ses_id']
        exp = check['expires']
    return sesh, exp


async def rem_chat(chat_id):
    check = await is_chat(chat_id)
    if check:
        cli.delete_one({'chat_id': chat_id})
    return True


async def get_all_chats(chat_id):
    return cli.find({'chat_id': chatid})
