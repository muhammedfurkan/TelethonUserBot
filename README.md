
## TelegramUserBot ❤️️

[![Sourcery](https://img.shields.io/badge/Sourcery-enabled-brightgreen)](https://sourcery.ai)

|Deploy To Heroku|  Gitpod Online|
|--|--|
| [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/muhammedfurkan/TelethonUserBot) | [![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/mmuhammedfurkan/TelethonUserBot) |

### DeepSource


[![DeepSource](https://deepsource.io/gh/muhammedfurkan/TelethonUserBot.svg/?label=active+issues&show_trend=true)](https://deepsource.io/gh/muhammedfurkan/TelethonUserBot/?ref=repository-badge)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[![DeepSource](https://deepsource.io/gh/muhammedfurkan/TelethonUserBot.svg/?label=resolved+issues&show_trend=true)](https://deepsource.io/gh/muhammedfurkan/TelethonUserBot/?ref=repository-badge)


### Setting Up Locally 👇🏻

 - Fill in the required fields in **"sample_config.py"**
 - Install the required libraries with **requirements.txt**.
( `pip3 install -r requirements.txt` )

 - And then start the bot. ( `python3 -m userbot` )
 - If you did it correctly, the bot will run successfully.


### Create String Session

[![Run on Repl.it](https://repl.it/badge/github/jasonalantolbert/replit-badger)](https://repl.it/@furki/telegram-session)

### Example Plugin

  ```python
  from  datetime  import  datetime
from userbot import bot
from userbot.util import admin_cmd

@bot.on(admin_cmd(pattern="ping"))
async def ping(event):
	start  =  datetime.now()
	await  event.edit("Pong!")
	end  =  datetime.now()
	ms  = (end  -  start).microseconds  /  1000
	await  event.edit("Pong!\n`{}`".format(ms))
```

### Contact ✍️
If you run into any problems, feel free to let me know. You can contact me using [this link](https://t.me/By_Azade).

### License ⚠️
-   Copyright (C) 2020 by  [M.Furkan](https://github.com/Muhammedfurkan)  ❤️️
-   Licensed under the terms of the  [Mozilla Public License 2.0](https://github.com/muhammedfurkan/TelethonUserBot/blob/master/LICENSE)
