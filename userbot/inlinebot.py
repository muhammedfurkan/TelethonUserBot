import asyncio
import json
import logging
import os
import re
from math import ceil

from sample_config import Config
from telethon import custom, events

from userbot import bot, tgbot
from userbot.util import humanbytes


# if Config.TG_BOT_USER_NAME_BF_HER is not None and tgbot is not None:
@tgbot.on(events.InlineQuery)
async def inline_handler(event):
    me = await bot.get_me()
    builder = event.builder
    result = None
    query = event.text
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    if query.startswith("ytdl"):
        # input format should be ytdl URL
        p = re.compile("ytdl (.*)")
        r = p.search(query)
        ytdl_url = r.group(1).strip()
        if ytdl_url.startswith("http"):
            command_to_exec = [
                "youtube-dl",
                "--no-warnings",
                "--youtube-skip-dash-manifest",
                "-j",
                ytdl_url
            ]
            logging.info(command_to_exec)
            process = await asyncio.create_subprocess_exec(
                *command_to_exec,
                # stdout must a pipe to be accessible as process.stdout
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            # Wait for the subprocess to finish
            stdout, stderr = await process.communicate()
            e_response = stderr.decode().strip()
            # logger.info(e_response)
            t_response = stdout.decode().strip()
            logging.info(command_to_exec)
            if e_response:
                error_message = e_response.replace(
                    "please report this issue on https://yt-dl.org/bug . Make sure you are using the latest version; see  https://yt-dl.org/update  on how to update. Be sure to call youtube-dl with the --verbose flag and include its complete output.", "")
                # throw error
                result = builder.article(
                    "YTDL Errors © @UserBot",
                    text=f"{error_message} Powered by @UserBot",
                    link_preview=False
                )
            elif t_response:
                x_reponse = t_response
                if "\n" in x_reponse:
                    x_reponse, _ = x_reponse.split("\n")
                response_json = json.loads(x_reponse)
                save_ytdl_json_path = Config.TMP_DOWNLOAD_DIRECTORY + \
                    "/" + "YouTubeDL" + ".json"
                with open(save_ytdl_json_path, "w", encoding="utf8") as outfile:
                    json.dump(response_json, outfile, ensure_ascii=False)
                # logger.info(response_json)
                inline_keyboard = []
                duration = None
                if "duration" in response_json:
                    duration = response_json["duration"]
                if "formats" in response_json:
                    for formats in response_json["formats"]:
                        format_id = formats.get("format_id")
                        format_string = formats.get("format_note")
                        if format_string is None:
                            format_string = formats.get("format")
                        format_ext = formats.get("ext")
                        approx_file_size = ""
                        if "filesize" in formats:
                            approx_file_size = humanbytes(
                                formats["filesize"])
                        cb_string_video = "ytdl|{}|{}|{}".format(
                            "video", format_id, format_ext)
                        if format_string is not None:
                            ikeyboard = [
                                custom.Button.inline(
                                    " " + format_ext + " video [" + format_string +
                                    "] ( " +
                                    approx_file_size + " )",
                                    data=(cb_string_video)
                                )
                            ]
                        else:
                            # special weird case :\
                            ikeyboard = [
                                custom.Button.inline(
                                    " " + approx_file_size + " ",
                                    data=cb_string_video
                                )
                            ]
                        inline_keyboard.append(ikeyboard)
                    if duration is not None:
                        cb_string_64 = "ytdl|{}|{}|{}".format(
                            "audio", "64k", "mp3")
                        cb_string_128 = "ytdl|{}|{}|{}".format(
                            "audio", "128k", "mp3")
                        cb_string = "ytdl|{}|{}|{}".format(
                            "audio", "320k", "mp3")
                        inline_keyboard.append([
                            custom.Button.inline(
                                "MP3 " + "(" + "64 kbps" + ")", data=cb_string_64
                            ),
                            custom.Button.inline(
                                "MP3 " + "(" + "128 kbps" + ")", data=cb_string_128
                            )
                        ])
                        inline_keyboard.append([
                            custom.Button.inline(
                                "MP3 " + "(" + "320 kbps" + ")", data=cb_string
                            )
                        ])
                else:
                    format_id = response_json["format_id"]
                    format_ext = response_json["ext"]
                    cb_string_video = "ytdl|{}|{}|{}".format(
                        "video", format_id, format_ext)
                    inline_keyboard.append([
                        custom.Button.inline(
                            "video",
                            data=cb_string_video
                        )
                    ])
                result = builder.article(
                    "YouTube © UserBOT",
                    text=f"{ytdl_url} powered by UserBOT",
                    buttons=inline_keyboard,
                    link_preview=True
                )
    else:
        result = builder.article(
            "© UserBOT",
            text=(
                "Try UserBOT\n"
                "You can log-in as Bot or User and do many cool things with your Telegram account.\n\n"
                "All instaructions to run UserBOT in your PC has been explained in https://github.com/muhammedfurkan/TelethonUserBot"
            ),
            buttons=[
                [custom.Button.url("Join the Channel", "https://telegram.dog/telethon"), custom.Button.url(
                    "Join the Group", "tg://some_unsupported_feature")],
                [custom.Button.url(
                    "Source Code", "tg://some_unsupported_feature")]
            ],
            link_preview=False
        )
    await event.answer([result] if result else None)


def paginate_help(page_number, loaded_plugins, prefix):
    number_of_rows = Config.NO_OF_BUTTONS_DISPLAYED_IN_H_ME_CMD
    number_of_cols = 2
    helpable_plugins = [p for p in loaded_plugins if not p.startswith("_")]
    helpable_plugins = sorted(helpable_plugins)
    modules = [custom.Button.inline(
        "{} {}".format("✅", x),
        data="ub_plugin_{}".format(x))
        for x in helpable_plugins]
    pairs = list(zip(modules[::number_of_cols], modules[1::number_of_cols]))
    if len(modules) % number_of_cols == 1:
        pairs.append((modules[-1],))
    max_num_pages = ceil(len(pairs) / number_of_rows)
    modulo_page = page_number % max_num_pages
    if len(pairs) > number_of_rows:
        pairs = pairs[modulo_page * number_of_rows:number_of_rows * (modulo_page + 1)] + \
            [
            (custom.Button.inline("Previous", data="{}_prev({})".format(prefix, modulo_page)),
             custom.Button.inline("Next", data="{}_next({})".format(prefix, modulo_page)))
        ]
    return pairs
