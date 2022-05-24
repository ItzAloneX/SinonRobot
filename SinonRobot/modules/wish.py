import random
from PIL import Image
from SinonRobot import telethn as sinon
from telethon import events
@sinon.on(events.NewMessage(pattern="/wish ?(.*)"))
async def wish(e):

 if e.is_reply:
         mm = random.randint(1,100)
         lol = await e.get_reply_message()
         fire = "https://telegra.ph/file/49b30183c55c30d9c46c1.jpg"
         await sinon.send_file(e.chat_id, fire,caption=f"**Hey [{e.sender.first_name}](tg://user?id={e.sender.id}), Your wish has been cast.💜**\n\n__chance of success {mm}%__", reply_to=lol)
 if not e.is_reply:
         mm = random.randint(1,100)
         fire = "https://telegra.ph/file/49b30183c55c30d9c46c1.jpg"
         await sinon.send_file(e.chat_id, fire,caption=f"**Hey [{e.sender.first_name}](tg://user?id={e.sender.id}), Your wish has been cast.💜**\n\n__chance of success {mm}%__", reply_to=e)
