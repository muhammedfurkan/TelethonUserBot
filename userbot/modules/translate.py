""" Google Translate
Available Commands:
.tr LanguageCode as reply to a message
.tr LangaugeCode | text to translate"""


# from googletrans import LANGUAGES, Translator
from gpytranslate import Translator

from userbot import bot
from userbot.util import admin_cmd


@bot.on(admin_cmd(pattern="tr ?(.*)"))
async def _(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        text = previous_message.message
        lan = input_str or "en"
    elif "|" in input_str:
        lan, text = input_str.split("|")
    else:
        await event.edit("`.tr LanguageCode` as reply to a message")
        return
    # text = emoji.demojize(text.strip()) # No need this.
    lan = lan.strip()
    translator = Translator()
    try:
        translated = await translator(text, targetlang=lan)

        after_tr_text = translated.text
        source_lan = await translator.detect(f'{translated.orig}')
        transl_lan = await translator.detect(f'{translated.text}')
        output_str = "Detected Language: **{}**\nTRANSLATED To: **{}**\n\n{}".format(
            source_lan,
            transl_lan,
            after_tr_text
        )
        await event.edit(output_str)
    except Exception as exc:
        await event.edit(str(exc))
