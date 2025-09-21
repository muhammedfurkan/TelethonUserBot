""" Unblock blocked bots and users
Syntax: .engelkaldir bot - Unblocks all blocked bots
Syntax: .engelkaldir user - Unblocks all blocked users
"""
import asyncio
import logging

from telethon import errors, functions, types
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
                # Check if user is not deleted and categorize
                if hasattr(user_obj, 'deleted') and user_obj.deleted:
                    continue  # Skip deleted accounts
                
                if hasattr(user_obj, 'bot') and user_obj.bot:
                    bot_count += 1
                    bots.append(user_obj.id)
                else:
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
            failed_count = 0
            total_bots = len(bots)
            
            for i, bot_id in enumerate(bots):
                try:
                    bot_entity = await event.client.get_entity(bot_id)
                    await event.client(functions.contacts.UnblockRequest(
                        id=bot_entity,
                        my_stories_from=True
                    ))
                    unblocked_count += 1
                    
                    # Update progress every 5 bots
                    if (i + 1) % 5 == 0:
                        await event.edit(f"**İşleniyor...** {i + 1}/{total_bots} bot işlendi")
                    
                    # Add small delay between operations to avoid rate limiting
                    if i < total_bots - 1:  # Don't sleep after the last one
                        await asyncio.sleep(0.5)
                        
                except errors.FloodWaitError as e:
                    logger.warning(f"FloodWait error for bot {bot_id}: {e.seconds} seconds")
                    await event.edit(f"**⏳ Telegram limiti:** {e.seconds} saniye bekleniyor... ({i + 1}/{total_bots})")
                    await asyncio.sleep(e.seconds)
                    
                    # Retry the same bot after waiting
                    try:
                        bot_entity = await event.client.get_entity(bot_id)
                        await event.client(functions.contacts.UnblockRequest(
                            id=bot_entity,
                            my_stories_from=True
                        ))
                        unblocked_count += 1
                    except Exception as retry_e:
                        logger.warning(f"Error retrying bot {bot_id}: {retry_e}")
                        failed_count += 1
                        
                except Exception as e:
                    logger.warning(f"Error unblocking bot {bot_id}: {e}")
                    failed_count += 1
                    continue
            
            if failed_count > 0:
                await event.edit(f"**✅ {unblocked_count}/{total_bots} bot engelini kaldırıldı.**\n**⚠️ {failed_count} bot işlenemedi.**")
            else:
                await event.edit(f"**✅ {unblocked_count}/{total_bots} bot engelini kaldırıldı.**")
        
        elif input_str == 'user':
            if not users:
                await event.edit("**Engellenmiş kullanıcı bulunamadı.**")
                return
            
            unblocked_count = 0
            failed_count = 0
            total_users = len(users)
            
            for i, user_id in enumerate(users):
                try:
                    user_entity = await event.client.get_entity(user_id)
                    await event.client(functions.contacts.UnblockRequest(
                        id=user_entity,
                        my_stories_from=True
                    ))
                    unblocked_count += 1
                    
                    # Update progress every 5 users
                    if (i + 1) % 5 == 0:
                        await event.edit(f"**İşleniyor...** {i + 1}/{total_users} kullanıcı işlendi")
                    
                    # Add small delay between operations to avoid rate limiting
                    if i < total_users - 1:  # Don't sleep after the last one
                        await asyncio.sleep(0.5)
                        
                except errors.FloodWaitError as e:
                    logger.warning(f"FloodWait error for user {user_id}: {e.seconds} seconds")
                    await event.edit(f"**⏳ Telegram limiti:** {e.seconds} saniye bekleniyor... ({i + 1}/{total_users})")
                    await asyncio.sleep(e.seconds)
                    
                    # Retry the same user after waiting
                    try:
                        user_entity = await event.client.get_entity(user_id)
                        await event.client(functions.contacts.UnblockRequest(
                            id=user_entity,
                            my_stories_from=True
                        ))
                        unblocked_count += 1
                    except Exception as retry_e:
                        logger.warning(f"Error retrying user {user_id}: {retry_e}")
                        failed_count += 1
                        
                except Exception as e:
                    logger.warning(f"Error unblocking user {user_id}: {e}")
                    failed_count += 1
                    continue
            
            if failed_count > 0:
                await event.edit(f"**✅ {unblocked_count}/{total_users} kullanıcının engeli kaldırıldı.**\n**⚠️ {failed_count} kullanıcı işlenemedi.**")
            else:
                await event.edit(f"**✅ {unblocked_count}/{total_users} kullanıcının engeli kaldırıldı.**")
    
    except Exception as e:
        await event.edit(f"**❌ Hata:** `{str(e)}`")
        logger.error(f"Error in engelkaldir command: {e}")