from userbot.database.mongo import cli

cli = cli["Userbot"]["Storage"]


async def save_file(name, path, file):
    return cli.insert_one({"Name": name, "Path": path, "File": file})


async def update_file(name, path, newfile):
    return cli.update_one(
        {"Name": name}, {"$set": {"File": newfile, "Path": path}})


async def check():
    return (False if not list(cli.find({}, {"File": 0}))
            else list(cli.find({}, {"File": 0})))


async def retrieve():
    return (False if not list(cli.find({}))
            else list(cli.find({})))


async def check_one(name):
    return bool(cli.find_one({"Name": name}))


async def delete():
    return cli.delete_many({})


async def delete_one(name):
    return cli.delete_one({"Name": name})
