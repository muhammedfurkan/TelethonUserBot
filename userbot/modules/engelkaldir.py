""" Unblock blocked bots and users
Syntax: .engelkaldir bot - Unblocks all blocked bots
Syntax: .engelkaldir user - Unblocks all blocked users
"""
import logging

from telethon import functions, types
from userbot import bot
from userbot.util import admin_cmd

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@bot.on(admin_cmd(pattern="engelkaldir ?(.*)"))
async def unblock_users_or_bots(event):
    if event.fwd_from:
        return
    
    input_str = event.pattern_match.group(1).strip().lower()
    
    if not input_str or input_str not in ['bot', 'user']:
        await event.edit("**Kullanım:** `.engelkaldir bot` veya `.engelkaldir user`")
        return
    
    await event.edit("**Engellenen hesaplar kontrol ediliyor...**")
    
    try:
        # Get blocked users
        result = await event.client(functions.contacts.GetBlockedRequest(
            offset=0,
            limit=10000,
            my_stories_from=False
        ))
        
        if not result.blocked:
            await event.edit("**Engellenmiş hesap bulunamadı.**")
            return
        
        bot_count = 0
        user_count = 0
        bots = []
        users = []
        
        # Categorize blocked accounts
        for blocked in result.blocked:
            try:
                user_obj = await event.client.get_entity(blocked.peer_id.user_id)
                if hasattr(user_obj, 'bot') and user_obj.bot and not getattr(user_obj, 'deleted', True):
                    bot_count += 1
                    bots.append(user_obj.id)
                elif not getattr(user_obj, 'deleted', True):
                    user_count += 1
                    users.append(user_obj.id)
            except Exception as e:
                logger.warning(f"Error processing blocked user {blocked.peer_id.user_id}: {e}")
                continue
        
        await event.edit(f"**Engellenen:** {user_count} kullanıcı, {bot_count} bot bulundu.\n**İşlem başlatılıyor...**")
        
        if input_str == 'bot':
            if not bots:
                await event.edit("**Engellenmiş bot bulunamadı.**")
                return
            
            unblocked_count = 0
            for bot_id in bots:
                try:
                    bot_entity = await event.client.get_entity(bot_id)
                    await event.client(functions.contacts.UnblockRequest(
                        id=bot_entity,
                        my_stories_from=True
                    ))
                    unblocked_count += 1
                except Exception as e:
                    logger.warning(f"Error unblocking bot {bot_id}: {e}")
                    continue
            
            await event.edit(f"**✅ {unblocked_count}/{len(bots)} bot engelini kaldırıldı.**")
        
        elif input_str == 'user':
            if not users:
                await event.edit("**Engellenmiş kullanıcı bulunamadı.**")
                return
            
            unblocked_count = 0
            for user_id in users:
                try:
                    user_entity = await event.client.get_entity(user_id)
                    await event.client(functions.contacts.UnblockRequest(
                        id=user_entity,
                        my_stories_from=True
                    ))
                    unblocked_count += 1
                except Exception as e:
                    logger.warning(f"Error unblocking user {user_id}: {e}")
                    continue
            
            await event.edit(f"**✅ {unblocked_count}/{len(users)} kullanıcının engeli kaldırıldı.**")
    
    except Exception as e:
        await event.edit(f"**❌ Hata:** `{str(e)}`")
        logger.error(f"Error in engelkaldir command: {e}")