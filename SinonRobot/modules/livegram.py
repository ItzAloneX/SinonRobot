from pyrogram import (
    Client,
    filters
)
from pyrogram.types import (
    Message
)
from SinonRobot import pbot as bot
from SinonRobot import OWNER_ID

@bot.on_message(
    filters.private
    & filters.incoming
 )
async def on_pm_s(client: Client, message: Message):
    if not message.from_user.id == 1732814103:
        fwded_mesg = await message.forward(
            chat_id=OWNER_ID,
            disable_notification=True
        )
