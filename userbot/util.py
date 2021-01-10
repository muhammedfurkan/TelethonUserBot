# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import asyncio
import datetime
import logging
import math
import os
import re
import shutil
import time
from typing import List

import aiohttp
from sample_config import Config
from telethon import events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.functions.messages import GetPeerDialogsRequest
from telethon.tl.tlobject import TLObject
from telethon.tl.types import (ChannelParticipantAdmin,
                               ChannelParticipantCreator,
                               MessageEntityPre)
from telethon.utils import add_surrogate

from userbot import bot
from userbot.modules import ALL_MODULES

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s", level=logging.WARNING
)
logger = logging.getLogger(__name__)
# from alive_progress import alive_bar

# the secret configuration specific things
ENV = bool(os.environ.get("ENV", False))
if ENV:
    from sample_config import Config
else:
    if os.path.exists("config.py"):
        from sample_config import Development as Config


def admin_cmd(**args):
    args["func"] = lambda e: e.via_bot_id is None

    pattern = args.get("pattern", None)
    allow_sudo = args.get("allow_sudo", False)

    # get the pattern from the decorator
    if pattern is not None:
        if pattern.startswith("\#"):
            # special fix for snip.py
            args["pattern"] = re.compile(pattern)
        else:
            args["pattern"] = re.compile(Config.COMMAND_HAND_LER + pattern)

    args["outgoing"] = True
    # should this command be available for other users?
    if allow_sudo:
        args["from_users"] = list(Config.SUDO_USERS)
        # Mutually exclusive with outgoing (can only set one of either).
        args["incoming"] = True
        del args["allow_sudo"]

    # error handling condition check
    elif "incoming" in args and not args["incoming"]:
        args["outgoing"] = True

    # add blacklist chats, UB should not respond in these chats
    args["blacklist_chats"] = True
    black_list_chats = list(Config.UB_BLACK_LIST_CHAT)
    if black_list_chats:
        args["chats"] = black_list_chats

    return events.NewMessage(**args)


async def is_read(bot, entity, message, is_out=None):
    """
    Returns True if the given message (or id) has been read
    if a id is given, is_out needs to be a bool
    """
    is_out = getattr(message, "out", is_out)
    if not isinstance(is_out, bool):
        raise ValueError(
            "Message was id but is_out not provided or not a bool")
    message_id = getattr(message, "id", message)
    if not isinstance(message_id, int):
        raise ValueError("Failed to extract id from message")

    dialog = (await bot(GetPeerDialogsRequest([entity]))).dialogs[0]
    max_id = dialog.read_outbox_max_id if is_out else dialog.read_inbox_max_id
    return message_id <= max_id


async def progress(current, total, event, start, type_of_ps):
    """Generic progress_callback for both
    upload.py and download.py"""
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        elapsed_time = round(diff)
        if elapsed_time == 0:
            return
        speed = current / diff
        time_to_completion = round((total - current) / speed)
        estimated_total_time = elapsed_time + time_to_completion
        progress_str = "[{0}{1}]\nPercent: {2}%\n".format(
            "".join("█" for _ in range(math.floor(percentage / 5))),
            "".join("░" for _ in range(20 - math.floor(percentage / 5))),
            round(percentage, 2),
        )

        tmp = progress_str + "{0} of {1}\nETA: {2}".format(
            humanbytes(current), humanbytes(
                total), time_formatter(estimated_total_time)
        )
        await event.edit("{}\n {}".format(type_of_ps, tmp))


def humanbytes(size):
    """Input size in bytes,
    outputs in a human readable format"""
    # https://stackoverflow.com/a/49361727/4723940
    if not size:
        return ""
    # 2 ** 10 = 1024
    power = 2 ** 10
    raised_to_pow = 0
    dict_power_n = {0: "", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        raised_to_pow += 1
    return str(round(size, 2)) + " " + dict_power_n[raised_to_pow] + "B"


def time_formatter(seconds: int) -> str:
    """Inputs time in seconds, to get beautified time,
    as string"""
    result = ""
    v_m = 0
    remainder = seconds
    r_ange_s = {"days": (24 * 60 * 60), "hours": (60 * 60),
                "minutes": 60, "seconds": 1}
    for age, divisor in r_ange_s.items():
        v_m, remainder = divmod(remainder, divisor)
        v_m = int(v_m)
        if v_m != 0:
            result += f" {v_m} {age} "
    return result


async def is_admin(client, chat_id, user_id):
    if not str(chat_id).startswith("-100"):
        return False
    try:
        req_jo = await client(GetParticipantRequest(channel=chat_id, user_id=user_id))
        chat_participant = req_jo.participant
        if isinstance(
            chat_participant, (ChannelParticipantCreator,
                               ChannelParticipantAdmin)
        ):
            return True
    except Exception:
        return False
    else:
        return False


# Not that Great but it will fix sudo reply
async def edit_or_reply(event, text):
    if event.sender_id not in Config.SUDO_USERS:
        return await event.edit(text)

    await event.delete()
    reply_to = await event.get_reply_message()
    if reply_to:
        return await reply_to.reply(text)
    else:
        return await event.reply(text)


async def run_command(command: List[str]) -> (str, str):
    process = await asyncio.create_subprocess_exec(
        *command,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    return t_response, e_response


async def take_screen_shot(video_file, output_directory, ttl):
    # https://stackoverflow.com/a/13891070/4723940
    out_put_file_name = output_directory + "/" + str(time.time()) + ".jpg"
    file_genertor_command = [
        "ffmpeg",
        "-ss",
        str(ttl),
        "-i",
        video_file,
        "-vframes",
        "1",
        out_put_file_name,
    ]
    # width = "90"
    t_response, e_response = await run_command(file_genertor_command)
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    logger.info(e_response)
    logger.info(t_response)
    return None


# https://github.com/Nekmo/telegram-upload/blob/master/telegram_upload/video.py#L26


async def cult_small_video(video_file, output_directory, start_time, end_time):
    # https://stackoverflow.com/a/13891070/4723940
    out_put_file_name = output_directory + \
        "/" + str(round(time.time())) + ".mp4"
    file_genertor_command = [
        "ffmpeg",
        "-i",
        video_file,
        "-ss",
        start_time,
        "-to",
        end_time,
        "-async",
        "1",
        "-strict",
        "-2",
        out_put_file_name,
    ]
    t_response, e_response = await run_command(file_genertor_command)
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    logger.info(e_response)
    logger.info(t_response)
    return None


# these two functions are stolen from
# https://github.com/udf/unibot/blob/kate/stdplugins/info.py


def parse_pre(text):
    text = text.strip()
    return (
        text,
        [MessageEntityPre(offset=0, length=len(
            add_surrogate(text)), language="")],
    )


def yaml_format(obj, indent=0, max_str_len=256, max_byte_len=64):
    """
    Pretty formats the given object as a YAML string which is returned.
    (based on TLObject.pretty_format)
    """
    result = []
    if isinstance(obj, TLObject):
        obj = obj.to_dict()

    if isinstance(obj, dict):
        if not obj:
            return "dict:"
        items = obj.items()
        has_items = len(items) > 1
        has_multiple_items = len(items) > 2
        result.append(obj.get("_", "dict") + (":" if has_items else ""))
        if has_multiple_items:
            result.append("\n")
            indent += 2
        for k, v in items:
            if k == "_" or v is None:
                continue
            formatted = yaml_format(v, indent)
            if not formatted.strip():
                continue
            result.append(" " * (indent if has_multiple_items else 1))
            result.append(f"{k}:")
            if not formatted[0].isspace():
                result.append(" ")
            result.append(f"{formatted}")
            result.append("\n")
        if has_items:
            result.pop()
        if has_multiple_items:
            indent -= 2
    elif isinstance(obj, str):
        # truncate long strings and display elipsis
        result = repr(obj[:max_str_len])
        if len(obj) > max_str_len:
            result += "…"
        return result
    elif isinstance(obj, bytes):
        # repr() bytes if it's printable, hex like "FF EE BB" otherwise
        if all(0x20 <= c < 0x7F for c in obj):
            return repr(obj)
        else:
            return (
                "<…>" if len(obj) > max_byte_len else " ".join(
                    f"{b:02X}" for b in obj)
            )
    elif isinstance(obj, datetime.datetime):
        # ISO-8601 without timezone offset (telethon dates are always UTC)
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    elif hasattr(obj, "__iter__"):
        # display iterables one after another at the base indentation level
        result.append("\n")
        indent += 2
        for x in obj:
            result.append(f"{' ' * indent}- {yaml_format(x, indent + 2)}")
            result.append("\n")
        result.pop()
        indent -= 2
    else:
        return repr(obj)

    return "".join(result)


# NOTE Ectract tool
def extract_all(archives, extract_path):
    for filename in archives:
        shutil.unpack_archive(filename, extract_path)


def load_module(shortname):
    if shortname.startswith("__"):
        pass
    elif shortname.endswith("_"):
        import importlib
        import sys
        from pathlib import Path
        path = Path(f"userbot/modules/{shortname}.py")
        name = "userbot.modules.{}".format(shortname)
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        print("Successfully (re)imported "+shortname)
    else:
        import importlib
        import sys
        from pathlib import Path
        path = Path(f"userbot/modules/{shortname}.py")
        name = "userbot.modules.{}".format(shortname)
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        mod.bot = bot
        mod.logger = logging.getLogger(shortname)
        mod.Config = Config
        mod.borg = bot
        spec.loader.exec_module(mod)
        sys.modules["userbot.modules."+shortname] = mod
        print("UserBot Modules Successfully Loaded "+shortname)


def remove_plugin(shortname):
    try:
        try:
            for i in ALL_MODULES[shortname]:
                bot.remove_event_handler(i)
            del ALL_MODULES[shortname]
            # print(f"removed plugin {shortname}")
        except:
            name = f"userbot.modules.{shortname}"

            for i in reversed(range(len(bot._event_builders))):
                ev, cb = bot._event_builders[i]
                if cb.__module__ == name:
                    del bot._event_builders[i]
    except:
        raise ValueError


class AioHttp:
    @staticmethod
    async def get_json(link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                return await resp.json()

    @staticmethod
    async def get_text(link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                return await resp.text()

    @staticmethod
    async def get_raw(link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                return await resp.read()
