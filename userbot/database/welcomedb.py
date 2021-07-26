
from userbot.database.mongo import cli

cli = cli["Userbot"]["welcome"]


async def get_current_welcome_settings(chat_id):
    return cli.find_one({'chat_id': chat_id})


async def add_welcome_setting(chat_id, should_clean_welcome, previous_welcome, f_mesg_id):
    check = await get_current_welcome_settings(chat_id)
    if not check:
        cli.insert_one(
            {
                'chat_id': chat_id,
                'should_clean_welcome': should_clean_welcome,
                'previous_welcome': previous_welcome,
                'f_mesg_id': f_mesg_id
            }
        )
        return True
    cli.update_one(
        {
            '_id': check['_id'],
            'chat_id': check['chat_id'],
            'should_clean_welcome': should_clean_welcome,
            'previous_welcome': check['previous_welcome']
        }, {'$set': {
            'f_mesg_id': f_mesg_id
        }}
    )
    return False


async def rm_welcome_setting(chat_id):
    to_check = await get_current_welcome_settings(chat_id)

    if not to_check:
        return False
    cli.delete_one({
        '_id': to_check["_id"],
        'chat_id': to_check["chat_id"],
        'should_clean_welcome': to_check["should_clean_welcome"],
        'previous_welcome': to_check['previous_welcome'],
        'f_mesg_id': to_check['f_mesg_id']
    })

    return True
