from userbot.database.mongo import cli

cli = cli["Userbot"]["Weather"]

# Weather


async def get_weather():
    return cli.find_one({'weather_city': {
        '$exists': True
    }}, {'weather_city': 1})


async def set_weather(city):
    to_check = await get_weather()

    if to_check:
        cli.update_one(
            {
                '_id': to_check['_id'],
                'weather_city': to_check['weather_city']
            }, {"$set": {
                'weather_city': city
            }})
    else:
        cli.insert_one({'weather_city': city})
