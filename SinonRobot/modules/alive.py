from telethon import events, Button, custom
import re, os
from SinonRobot.events import register
from SinonRobot import telethn as tbot
from SinonRobot import telethn as tgbot
PHOTO = "https://telegra.ph/file/1f11d35c2002ffac502f9.jpg"
@register(pattern=("/alive"))
async def awake(event):
  SINON = f"**♡ hey {event.sender.first_name} I,m Sinon** \n\n"
  SINON += "**♡ I'm Working Property**\n\n"
  SINON += "**♡ Sinon: LATEST Version**\n\n"
  SINON += "**♡ My Creator:** [Alone X](t.meItzAloneX)\n\n"
  SINON += "**♡ python-Telegram-Bot: 13.11**\n\n"
  BUTTON = [[Button.url("🗯️ Support", "https://t.me/SinonSupport"), Button.url("🔔 Updates", "https://t.me/SinonUpdates")]]
  await tbot.send_file(event.chat_id, PHOTO, caption=SINON,  buttons=BUTTON)
