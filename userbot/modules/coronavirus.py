"""CoronaVirus LookUp
Syntax: .coronavirus <country>"""
from covid import Covid

from userbot import bot
from userbot.util import admin_cmd, register


@bot.on(admin_cmd(pattern="corona (.*)"))
async def _(event):
    covid = Covid()
    data = covid.get_data()
    country = event.pattern_match.group(1)
    country_data = get_country_data(country, data)
    # output_text = ""
    # for name, value in country_data.items():
    # output_text += "`{}`: `{}`\n".format(str(name), str(value))
    # await event.edit("**CoronaVirus Info in {}**:\n\n{}".format(country.capitalize(), output_text))
    try:
        ulke = country_data['country']
        onaylanan = country_data['confirmed']
        aktif = country_data['active']
        olum = country_data['deaths']
        tedavi = country_data['recovered']
        msg = "**Corona Virus Bilgileri**\n\nÜlke: {}\nOnaylanan Vaka: {}\nAktif Vaka: {}\nÖlümle Sonuçlanan Vaka: {}\nTedavi Edilen Vaka: {}".format(
            ulke, onaylanan, aktif, olum, tedavi)
        await event.edit(msg)
    except KeyError as e:
        await event.edit("Ülke ismini yanlış girdin. {}".format(e))


def get_country_data(country, world):
    for country_data in world:
        if country_data["country"].lower() == country.lower():
            return country_data
    return {"Status": "No information yet about this country!"}
