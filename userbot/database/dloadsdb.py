from userbot.database.mongo import cli

cli = cli["Userbot"]["Dloads"]


async def dload(name, link):
    return cli.insert_one({"Name": name, "URL": link})


async def unload(name):
    return cli.delete_one({"Name": name})


async def check_dload():
    return (False if not cli.find({"Name": {"$exists": True}})
            else cli.find({"Name": {"$exists": True}}))


async def delete(name):
    return cli.delete_one({name: {"$exists": True}})
