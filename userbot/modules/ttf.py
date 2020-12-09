
from userbot import bot
from userbot.util import admin_cmd, register


@bot.on(admin_cmd(pattern="ttf ?(.*)"))
async def get(event):
    name = event.text[5:] + ".txt"
    m = await event.get_reply_message()
    with open(name, "w") as f:
        f.write(m.text)
    await event.delete()
    await bot.send_file(event.chat_id, name, force_document=True)
