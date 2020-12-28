"""Get weather data using OpenWeatherMap
Syntax: .weather <Location> """
import io
import json
import logging
import time
from datetime import datetime, tzinfo

import aiohttp
import requests
from pytz import country_names as c_n
from pytz import country_timezones as c_tz
from pytz import timezone as tz
from sample_config import Config
from userbot import bot
from userbot.database.weatherdb import get_weather, set_weather
from userbot.util import admin_cmd

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


# ====================
async def get_tz(con):
    """
    Get time zone of the given country.
    Credits: @aragon12 and @zakaryan2004.
    """
    for c_code in c_n:
        if con == c_n[c_code]:
            return tz(c_tz[c_code][0])
    try:
        if c_n[con]:
            return tz(c_tz[con][0])
    except KeyError:
        return


@bot.on(admin_cmd(pattern="weather (.*)"))
async def fetch_weather(weather):
    """ For .weather command, gets the current weather of a city. """
    if Config.OPEN_WEATHER_MAP_APPID is None:
        await weather.edit("Please set OPEN_WEATHER_MAP_APPID")
        return

    OpenWeatherAPI = Config.OPEN_WEATHER_MAP_APPID
    saved_props = await get_weather()

    if not weather.pattern_match.group(1):
        if 'weather_city' in saved_props:
            city = saved_props['weather_city']
        else:
            await weather.edit("`Please specify a city or set one as default.`")
            return
    else:
        city = weather.pattern_match.group(1)

    timezone_countries = {
        timezone: country
        for country, timezones in c_tz.items() for timezone in timezones
    }

    if "," in city:
        newcity = city.split(",")
        if len(newcity[1]) == 2:
            city = newcity[0].strip() + "," + newcity[1].strip()
        else:
            country = await get_tz((newcity[1].strip()).title())
            try:
                countrycode = timezone_countries[f'{country}']
            except KeyError:
                await weather.edit("Invalid paramater")
                return
            city = newcity[0].strip() + "," + countrycode.strip()

    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OpenWeatherAPI}'
    request = requests.get(url)
    result = json.loads(request.text)

    if request.status_code != 200:
        await weather.edit("Invalid parameter")
        return

    cityname = result['name']
    curtemp = result['main']['temp']
    humidity = result['main']['humidity']
    min_temp = result['main']['temp_min']
    max_temp = result['main']['temp_max']
    desc = result['weather'][0]
    desc = desc['main']
    country = result['sys']['country']
    sunrise = result['sys']['sunrise']
    sunset = result['sys']['sunset']
    wind = result['wind']['speed']
    winddir = result['wind']['deg']

    ctimezone = tz(c_tz[country][0])
    time = datetime.now(ctimezone).strftime("%A, %I:%M %p")
    fullc_n = c_n[f"{country}"]
    # dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    #        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

    div = (360 / len(dirs))
    funmath = int((winddir + (div / 2)) / div)
    findir = dirs[funmath % len(dirs)]
    kmph = str(wind * 3.6).split(".")
    mph = str(wind * 2.237).split(".")

    def fahrenheit(fahr):
        temp = str(((fahr - 273.15) * 9 / 5 + 32)).split(".")
        return temp[0]

    def celsius(celc):
        temp = str((celc - 273.15)).split(".")
        return temp[0]

    def sun(unix):
        return datetime.fromtimestamp(
            unix, tz=ctimezone).strftime("%I:%M %p")

    await weather.edit(
        f"**Temperature:** `{celsius(curtemp)}°C | {fahrenheit(curtemp)}°F`\n"
        +
        f"**Min. Temp.:** `{celsius(min_temp)}°C | {fahrenheit(min_temp)}°F`\n"
        +
        f"**Max. Temp.:** `{celsius(max_temp)}°C | {fahrenheit(max_temp)}°F`\n"
        + f"**Humidity:** `{humidity}%`\n" +
        f"**Wind:** `{kmph[0]} kmh | {mph[0]} mph, {findir}`\n" +
        f"**Sunrise:** `{sun(sunrise)}`\n" +
        f"**Sunset:** `{sun(sunset)}`\n\n\n" + f"**{desc}**\n" +
        f"`{cityname}, {fullc_n}`\n" + f"`{time}`")


@bot.on(admin_cmd(pattern="setcity ?(.*)"))
async def set_default_city(city):
    """ For .setcity command, change the default
        city for weather command. """

    if Config.OPEN_WEATHER_MAP_APPID is None:
        await city.edit("Please set OPEN_WEATHER_MAP_APPID")
        return

    OpenWeatherAPI = Config.OPEN_WEATHER_MAP_APPID

    if not city.pattern_match.group(1):
        await city.edit("`Please specify a city to set one as default.`")
        return
    else:
        city_name = city.pattern_match.group(1)

    timezone_countries = {
        timezone: country
        for country, timezones in c_tz.items() for timezone in timezones
    }

    if "," in city_name:
        newcity = city_name.split(",")
        if len(newcity[1]) == 2:
            city_name = newcity[0].strip() + "," + newcity[1].strip()
        else:
            country = await get_tz((newcity[1].strip()).title())
            try:
                countrycode = timezone_countries[f'{country}']
            except KeyError:
                await city.edit("Invalid parameter")
                return
            city_name = newcity[0].strip() + "," + countrycode.strip()

    url = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OpenWeatherAPI}'
    request = requests.get(url)
    result = json.loads(request.text)

    if request.status_code != 200:
        await city.edit("Invalid paramater")
        return

    await set_weather(city_name)
    cityname = result['name']
    country = result['sys']['country']

    fullc_n = c_n[f"{country}"]

    await city.edit(f"`Set default city as {cityname}, {fullc_n}.`")


@bot.on(admin_cmd(pattern="wttr (.*)"))
async def _(event):
    if event.fwd_from:
        return
    sample_url = "https://wttr.in/{}.png"
    # logger.info(sample_url)
    input_str = event.pattern_match.group(1)
    async with aiohttp.ClientSession() as session:
        response_api_zero = await session.get(sample_url.format(input_str))
        # logger.info(response_api_zero)
        response_api = await response_api_zero.read()
        with io.BytesIO(response_api) as out_file:
            await event.reply(
                file=out_file
            )
    await event.edit(input_str)
