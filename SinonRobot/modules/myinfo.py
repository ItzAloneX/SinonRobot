from telethon import events, Button, custom, version
from telethon.tl.types import ChannelParticipantsAdmins
import asyncio
import os,re
import requests
import datetime
import time
from datetime import datetime
import random
from PIL import Image
from io import BytesIO
from SinonRobot import telethn as bot
from SinonRobot import telethn as tgbot
from SinonRobot.events import register
from SinonRobot import dispatcher


edit_time = 5
""" =======================CONSTANTS====================== """
file1 = "https://telegra.ph/file/605e0e2d93f9a338e2ea8.jpg"
file2 = "https://telegra.ph/file/ba8f14b3119948b4b1a8b.jpg"
file3 = "https://telegra.ph/file/4d1fee917b01de0df08ec.jpg"
file4 = "https://telegra.ph/file/49b30183c55c30d9c46c1.jpg"
file5 = "https://telegra.ph/file/9cc44f109dc815d92b014.jpg"
""" =======================CONSTANTS====================== """

@register(pattern="/myinfo")
async def proboyx(event):
    chat = await event.get_chat()
    current_time = datetime.utcnow()
    betsy = event.sender.first_name
    button = [[custom.Button.inline("Click Here",data="information")]]
    on = await bot.send_file(event.chat_id, file=file2,caption= f"♡ Hey {betsy}, I'm Sinon \n♡ I'm Created By [Alone X](t.me/ItzAloneX)\n♡ Click The Button Below To Get Your Info", buttons=button)

    await asyncio.sleep(edit_time)
    ok = await bot.edit_message(event.chat_id, on, file=file3, buttons=button) 

    await asyncio.sleep(edit_time)
    ok2 = await bot.edit_message(event.chat_id, ok, file=file5, buttons=button)

    await asyncio.sleep(edit_time)
    ok3 = await bot.edit_message(event.chat_id, ok2, file=file1, buttons=button)

    await asyncio.sleep(edit_time)
    ok7 = await bot.edit_message(event.chat_id, ok6, file=file4, buttons=button)
    
    await asyncio.sleep(edit_time)
    ok4 = await bot.edit_message(event.chat_id, ok3, file=file2, buttons=button)
    
    await asyncio.sleep(edit_time)
    ok5 = await bot.edit_message(event.chat_id, ok4, file=file1, buttons=button)
    
    await asyncio.sleep(edit_time)
    ok6 = await bot.edit_message(event.chat_id, ok5, file=file3, buttons=button)
    
    await asyncio.sleep(edit_time)
    ok7 = await bot.edit_message(event.chat_id, ok6, file=file5, buttons=button)

    await asyncio.sleep(edit_time)
    ok7 = await bot.edit_message(event.chat_id, ok6, file=file4, buttons=button)

@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"information")))
async def callback_query_handler(event):
  try:
    boy = event.sender_id
    PRO = await bot.get_entity(boy)
    SINON = "💕 YOUR DETAILS BY SINON \n\n"
    SINON += f"♡ FIRST NAME : {PRO.first_name} \n"
    SINON += f"♡ LAST NAME : {PRO.last_name}\n"
    SINON += f"♡ YOU BOT : {PRO.bot} \n"
    SINON += f"♡ RESTRICTED : {PRO.restricted} \n"
    SINON += f"♡ USER ID : {boy}\n"
    SINON += f"♡ USERNAME : {PRO.username}\n"
    await event.answer(SINON, alert=True)
  except Exception as e:
    await event.reply(f"{e}")

__help__ = """
♡ `/myinfo`*:* shows your info in inline button

*♡ Powered By :- @YatoNetwork*
"""

__mod_name__ = "My-Info"
__command_list__ = [
    "myinfo"
]
