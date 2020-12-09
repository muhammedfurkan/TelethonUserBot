from database.mongo import cli

cli = cli["Userbot"]["Snips"]


async def add(key, value):
    return cli.insert_one(
        {"Key": key, "Value": value})


async def others(opt):
    return cli.insert_one({"Others": opt})


async def check():
    return (False if not list(cli.find({}, {"Others": 0}))
            else list(cli.find({}, {"Others": 0})))


async def check_one(key):
    return (False if not cli.find_one({"Key": key})
            else cli.find_one({"Key": key}))


async def check_others():
    return not cli.find_one({"Others": False})


async def update(query, key, value):
    return cli.update_one(
        query, {"$set": {"Key": key, "Value": value}})


async def delete():
    return cli.delete_many({})


async def delete_one(key):
    return cli.delete_one({"Key": key})


async def delete_others():
    cli.delete_one({"Others": {"$exists": True}})
