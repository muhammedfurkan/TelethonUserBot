"""CC- @refundisillegal\nSyntax:-\n.get var NAME\n.del var NAME\n.set var NAME"""

import asyncio
import math
import os

import heroku3
import requests
from sample_config import Config
from userbot import bot
from userbot.bin.prettyjson import prettyjson
from userbot.util import admin_cmd, register

# =================
Heroku = heroku3.from_key(Config.HEROKU_API_KEY)
heroku_api = "https://api.heroku.com"
HEROKU_APP_NAME = Config.HEROKU_APP_NAME
HEROKU_API_KEY = Config.HEROKU_API_KEY

# Here lies the Magic


@bot.on(admin_cmd(pattern=r"(set|get|del) var ?(.*)", allow_sudo=True))
async def variable(var):
    if HEROKU_APP_NAME is not None:
        app = Heroku.app(HEROKU_APP_NAME)
    else:
        return await var.reply("`[HEROKU]:"
                               "\nPlease setup your` **HEROKU_APP_NAME**")
    exe = var.pattern_match.group(1)
    heroku_var = app.config()
    if exe in "get":
        await var.edit("`Getting information Bish...`")
        await asyncio.sleep(1.5)
        try:
            variable = var.pattern_match.group(2).split()[0]
            if variable in heroku_var:
                return await var.reply("**ConfigVars**:"
                                       f"\n\n**{variable}** = `{heroku_var[variable]}`\n")
            else:
                return await var.reply("**ConfigVars**:"
                                       f"\n\n`Error:\n-> {variable} don't exists`")
        except IndexError:
            configs = prettyjson(heroku_var.to_dict(), indent=2)
            with open("configs.json", "w") as fp:
                fp.write(configs)
            with open("configs.json", "r") as fp:
                result = fp.read()
                if len(result) >= 4096:
                    await var.client.send_file(
                        var.chat_id,
                        "configs.json",
                        reply_to=var.id,
                        caption="`Output too large, sending it as a file`",
                    )
                else:
                    await var.edit("`[HEROKU]` ConfigVars:\n\n"
                                   "================================"
                                   f"\n```{result}```\n"
                                   "================================"
                                   )
            os.remove("configs.json")
            return
    elif exe in "set":
        await var.edit("`Setting information...`")
        val = var.pattern_match.group(2).split()
        try:
            val[1]
        except IndexError:
            return await var.reply("`.set var <config name> <value>`")
        await asyncio.sleep(1.5)
        if val[0] in heroku_var:
            await var.reply(f"**{val[0]}**  `successfully changed to`  **{val[1]}**")
        else:
            await var.reply(f"**{val[0]}**  `successfully added with value: **{val[1]}**")
        heroku_var[val[0]] = val[1]
    elif exe in "del":
        await var.edit("`Getting information to deleting variable...`")
        try:
            variable = var.pattern_match.group(2).split()[0]
        except IndexError:
            return await var.reply("`Please specify ConfigVars you want to delete`")
        await asyncio.sleep(1.5)
        if variable in heroku_var:
            await var.reply(f"**{variable}**  `successfully deleted`")
            del heroku_var[variable]
        else:
            return await var.reply(f"**{variable}**  `is not exists`")


@bot.on(admin_cmd(pattern="usage ?(.*)", allow_sudo=True))
async def _(event):
    await event.edit("`Processing...`")
    useragent = ('Mozilla/5.0 (Linux; Android 10; SM-G975F) '
                 'AppleWebKit/537.36 (KHTML, like Gecko) '
                 'Chrome/80.0.3987.149 Mobile Safari/537.36'
                 )
    u_id = Heroku.account().id
    headers = {
        'User-Agent': useragent,
        'Authorization': f'Bearer {HEROKU_API_KEY}',
        'Accept': 'application/vnd.heroku+json; version=3.account-quotas',
    }
    path = "/accounts/" + u_id + "/actions/get-quota"
    r = requests.get(heroku_api + path, headers=headers)
    if r.status_code != 200:
        return await event.edit("`Error: something bad happened`\n\n"
                                f">.`{r.reason}`\n")
    result = r.json()
    quota = result['account_quota']
    quota_used = result['quota_used']

    """ - Used - """
    remaining_quota = quota - quota_used
    percentage = math.floor(remaining_quota / quota * 100)
    minutes_remaining = remaining_quota / 60
    hours = math.floor(minutes_remaining / 60)
    minutes = math.floor(minutes_remaining % 60)

    """ - Current - """
    App = result['apps']
    try:
        App[0]['quota_used']
    except IndexError:
        AppQuotaUsed = 0
        AppPercentage = 0
    else:
        AppQuotaUsed = App[0]['quota_used'] / 60
        AppPercentage = math.floor(App[0]['quota_used'] * 100 / quota)
    AppHours = math.floor(AppQuotaUsed / 60)
    AppMinutes = math.floor(AppQuotaUsed % 60)

    await asyncio.sleep(1.5)

    return await event.reply("**Dyno Usage**:\n\n"
                             f" -> `Dyno usage for`  **{HEROKU_APP_NAME}**:\n"
                             f"     •  `{AppHours}`**h**  `{AppMinutes}`**m**  "
                             f"**|**  [`{AppPercentage}`**%**]"
                             "\n"
                             " -> `Dyno hours quota remaining this month`:\n"
                             f"     •  `{hours}`**h**  `{minutes}`**m**  "
                             f"**|**  [`{percentage}`**%**]"
                             )


@bot.on(admin_cmd(pattern="logs"))
async def _(dyno):
    try:
        Heroku = heroku3.from_key(Config.HEROKU_API_KEY)
        app = Heroku.app(Config.HEROKU_APP_NAME)
    except BaseException:
        return await dyno.reply(" Please make sure your Heroku API Key, Your App name are configured correctly in the heroku var")
    await dyno.edit("Getting Logs....")
    with open('logs.txt', 'w') as log:
        log.write(app.get_log())
    await dyno.client.send_file(
        dyno.chat_id,
        "logs.txt",
        reply_to=dyno.id,
        caption="logs of 100+ lines",
    )
    await dyno.delete()
    return os.remove('logs.txt')


@bot.on(admin_cmd(pattern="dyno (on|restart|off|cancel deploy|cancel build) ?(.*)"))
async def dyno_manage(dyno):
    """ - Restart/Kill dyno - """
    await dyno.edit("`Sending information...`")
    app = Heroku.app(HEROKU_APP_NAME)
    exe = dyno.pattern_match.group(1)
    if exe in "on":
        try:
            Dyno = app.dynos()[0]
        except IndexError:
            app.scale_formation_process("worker", 1)
            text = f"`Starting` ⬢**{HEROKU_APP_NAME}**"
            sleep = 1
            dot = "."
            await dyno.edit(text)
            while (sleep <= 24):
                await dyno.edit(text + f"`{dot}`")
                await asyncio.sleep(1)
                if len(dot) == 3:
                    dot = "."
                else:
                    dot += "."
                sleep += 1
            state = Dyno.state
            if state in "up":
                await dyno.respond(f"⬢**{HEROKU_APP_NAME}** `up...`")
            elif state in "crashed":
                await dyno.respond(f"⬢**{HEROKU_APP_NAME}** `crashed...`")
            return await dyno.delete()
        else:
            return await dyno.edit(f"⬢**{HEROKU_APP_NAME}** `already on...`")
    if exe in "restart":
        try:
            """ - Catch error if dyno not on - """
            Dyno = app.dynos()[0]
        except IndexError:
            return await dyno.respond(f"⬢**{HEROKU_APP_NAME}** `is not on...`")
        else:
            text = f"`Restarting` ⬢**{HEROKU_APP_NAME}**"
            Dyno.restart()
            sleep = 1
            dot = "."
            await dyno.edit(text)
            while (sleep <= 24):
                await dyno.edit(text + f"`{dot}`")
                await asyncio.sleep(1)
                if len(dot) == 3:
                    dot = "."
                else:
                    dot += "."
                sleep += 1
            state = Dyno.state
            if state in "up":
                await dyno.respond(f"⬢**{HEROKU_APP_NAME}** `restarted...`")
            elif state in "crashed":
                await dyno.respond(f"⬢**{HEROKU_APP_NAME}** `crashed...`")
            return await dyno.delete()
    elif exe in "off":
        """ - Complete shutdown - """
        app.scale_formation_process("worker", 0)
        text = f"`Shutdown` ⬢**{HEROKU_APP_NAME}**"
        sleep = 1
        dot = "."
        while (sleep <= 3):
            await dyno.edit(text + f"`{dot}`")
            await asyncio.sleep(1)
            dot += "."
            sleep += 1
        await dyno.respond(f"⬢**{HEROKU_APP_NAME}** `turned off...`")
        return await dyno.delete()
    elif exe in "cancel deploy" or exe in "cancel build":
        """ - Only cancel 1 recent builds from activity - """
        build_id = dyno.pattern_match.group(2)
        if build_id is None:
            build = app.builds(order_by='created_at', sort='desc')[0]
        else:
            build = app.builds().get(build_id)
            if build is None:
                return await dyno.edit(
                    f"`There is no such build.id`:  **{build_id}**")
        if build.status != "pending":
            return await dyno.edit("`Zero active builds to cancel...`")
        useragent = ('Mozilla/5.0 (Linux; Android 10; SM-G975F) '
                     'AppleWebKit/537.36 (KHTML, like Gecko) '
                     'Chrome/80.0.3987.149 Mobile Safari/537.36'
                     )
        headers = {
            'User-Agent': useragent,
            'Authorization': f'Bearer {HEROKU_API_KEY}',
            'Accept': 'application/vnd.heroku+json; version=3.cancel-build',
        }
        path = "/apps/" + build.app.id + "/builds/" + build.id
        r = requests.delete(heroku_api + path, headers=headers)
        text = f"`Stopping build`  ⬢**{build.app.name}**"
        await dyno.edit(text)
        sleep = 1
        dot = "."
        await asyncio.sleep(2)
        while (sleep <= 3):
            await dyno.edit(text + f"`{dot}`")
            await asyncio.sleep(1)
            dot += "."
            sleep += 1
        await dyno.respond(
            "`[HEROKU]`\n"
            f"Build: ⬢**{build.app.name}**  `Stopped...`")
        """ - Restart main if builds cancelled - """
        try:
            app.dynos()[0].restart()
        except IndexError:
            await dyno.edit("`Your dyno main app is not on...`")
            await asyncio.sleep(2.5)
        return await dyno.delete()
