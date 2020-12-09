from userbot.database.mongo import cli

cli = cli["Userbot"]["AFK"]


async def set_afk(msg, time):
    return cli.insert_one({"Message": msg, "AFKTime": time})


async def set_godark(opt):
    return cli.insert_one({"GoDark": opt})


async def check_afk():
    return cli.find_one({"Message": {"$exists": True}})


async def check_godark():
    return cli.find_one({"GoDark": {"$exists": True}})


async def stop_afk():
    return cli.delete_one({"Message": {"$exists": True}})
