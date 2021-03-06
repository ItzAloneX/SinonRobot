import html
import os
import json
import importlib
import time
import re
import sys
import traceback
import SinonRobot.modules.sql.users_sql as sql
from sys import argv
from typing import Optional
from telegram import __version__ as peler
from platform import python_version as memek
from SinonRobot import (
    ALLOW_EXCL,
    CERT_PATH,
    DONATION_LINK,
    LOGGER,
    OWNER_ID,
    PORT,
    SUPPORT_CHAT,
    TOKEN,
    URL,
    WEBHOOK,
    SUPPORT_CHAT,
    dispatcher,
    StartTime,
    telethn,
    pbot,
    updater,
)

# needed to dynamically load modules
# NOTE: Module order is not guaranteed, specify that in the config file!
from SinonRobot.modules import ALL_MODULES
from SinonRobot.modules.helper_funcs.chat_status import is_user_admin
from SinonRobot.modules.helper_funcs.misc import paginate_modules
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop, run_async
from telegram.utils.helpers import escape_markdown


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


PM_START_TEXT = """
*⋆✦⋆────『 Sinon 詩乃 』────⋆✦⋆*
*♡ Hey!* *{}*
*♡ I'm Sinon An Anime Themed Powerful & Advanced Group Management Robot.*
*➖➖➖➖➖➖➖➖➖➖➖➖➖*
*♡ Try The Help Buttons Below To Know My Abilities.*

*♡ Powered By :- @YatoNetwork*[.](https://telegra.ph/file/12d50d9d064d6a985dabe.png)
"""

buttons = [
    [
        InlineKeyboardButton(text="🔐 Help​", callback_data="help_back"),
    ],
    [
        InlineKeyboardButton(text="🌺 About Me", callback_data="sinon_"),
        InlineKeyboardButton(text="👨🏻‍🔧 Basic Help", callback_data="sinon_basichelp"),
    ],
    [
        InlineKeyboardButton(text="🔄 Try Inline", switch_inline_query_current_chat=""),
    ],
    [
        InlineKeyboardButton(
            text="💕 Add Sinon To Your Group ",
            url=f"t.me/SinonRobot?startgroup=new",
        ),
    ],
]

HELP_STRINGS = """
*♡ Main Commands*

*♡* /help - *Click this to know about myself.*
*♡* /donate - *For Giving Donations To Me.*
*♡* /settings - *In PM : will send you your settings for all supported modules.*

*♡ In A Group : Will Redirect You To Pm With All That Chats Settings.
For All Commands Use* [/ or !](https://telegra.ph/file/073e002ac0acf1685f940.jpg)"""

SINON = """
*👋 Hi Again!  The name's Sinon \n\nA powerful group management bot built to help you manage your group easily.*
💕 Join [Sinon Support](https://t.me/SinonSupport) To Keep Yourself Updated About Sinon.
I have the Advanced Group Managing functions like flood control, a warning system etc but I mainly have the advanced and handy Antispam system and the SIBYL banning system which safegaurds and helps your group from spammers.
♡ I can restrict users.
♡ I can greet users with customizable welcome messages and even set a group's rules.
♡ I have an advanced anti-flood system.
♡ I can warn users until they reach max warns, with each predefined actions such as ban, mute, kick, etc.
♡ I have a note keeping system, blacklists, and even predetermined replies on certain keywords.
♡ I check for admins' permissions before executing any command and more stuffs
If you have any question about *Sinon*, let us know at @SinonSupport.
👇 You Can Know More About *Sinon* By Clicking The Below Buttons 👇"""

SINO_BASIC = """ *♡ Basic Setup Of Sinon*

1) First add Sinon to your group.

2) After adding promote sinon with full rights for fastest experience.

3) Next send /admincache in that group for refresh admin list in My Database.

*♡ All done, now check below buttons to know about use!* """

SINON_ADMIN = """
*Let's Make Your Group Bit Effective Now* 
♡ Congragulations, Sinon now ready to manage your group.
*Admin Tools*
♡ Basic Admin tools help you to protect and powerup your group.
♡ You can ban members, Kick members, Promote someone as admin through commands of bot.
*Welcome*
♡ Lets set a welcome message to welcome new users coming to your group.
♡ Send `/setwelcome [message]` to set a welcome message!"""

SINO_CMDS = [
    [
        InlineKeyboardButton(text="👷🏻‍♂️ Admin", callback_data="sinon_admin"),
        InlineKeyboardButton(text="📝 Notes", callback_data="sinon_notes"),
    ],
    [
        InlineKeyboardButton(text="🗯️ Support", callback_data="sinon_support"),
        InlineKeyboardButton(text="ℹ️ Credit", callback_data="sinon_credit"),
    ],
    [
        InlineKeyboardButton(text="💾 Source", callback_data="source_"),
    ],
    [
        InlineKeyboardButton(text="Back", callback_data="sinon_back"),              
    ],
]

DONATE_STRING = """*♡ Add Me To Your Chat That Is Donation For Me.*"""

HOWTOUSE = """
*♡ How To Use Sinon*
If You Can Also Add Sinon To Your Chats By Clicking [Here](http://t.me/SinonRobot?startgroup=true) And Selecting Chat.
You Can get support Sinon by joining [Support](https://t.me/Sinonsupport)."""

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("SinonRobot.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )


def test(update: Update, context: CallbackContext):
    # pprint(eval(str(update)))
    # update.effective_message.reply_text("Hola tester! _I_ *have* `markdown`", parse_mode=ParseMode.MARKDOWN)
    update.effective_message.reply_text("This person edited a message")
    print(update.effective_message)


def start(update: Update, context: CallbackContext):
    args = context.args
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="Go Back", callback_data="help_back"
                                )
                            ]
                        ]
                    ),
                )

            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                IMPORTED["rules"].send_rules(update, args[0], from_pm=True)

        else:
            first_name = update.effective_user.first_name
            update.effective_message.reply_text(
                PM_START_TEXT.format(
                    escape_markdown(first_name),
                    escape_markdown(uptime),
                    sql.num_users(),
                    sql.num_chats(),
                ),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
                disable_web_page_preview=True,
            )
    else:
        update.effective_message.reply_text(
            f"<b>Hi I'm Sinon</b>\n<b>Started working since:</b> <code>{uptime}</code>",
            parse_mode=ParseMode.HTML,
        )


def error_handler(update, context):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    message = (
        "An exception was raised while handling an update\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(tb),
    )

    if len(message) >= 4096:
        message = message[:4096]
    # Finally, send the message
    context.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.HTML)


# for test purposes
def error_callback(update: Update, context: CallbackContext):
    error = context.error
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print("no nono2")
        print("BadRequest caught")
        print(error)

        # handle malformed requests - read more below!
    except TimedOut:
        print("no nono3")
        # handle slow connection problems
    except NetworkError:
        print("no nono4")
        # handle other connection problems
    except ChatMigrated as err:
        print("no nono5")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors


def help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    print(query.message.chat.id)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "Here is the help for the *{}* module:\n".format(
                    SINON_BASIC[module].mod_name
                )
                + SINON_BASIC[module].sinon_basic
            )
            query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                  [
                    
                    [InlineKeyboardButton(text="Back", callback_data="help_back"), InlineKeyboardButton(text="🗯️ Support", url="t.me/SinonSupport")]
                  ]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_text(
                text=SINON_BASICC,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, SINON_BASIC, "sinonbasic")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_text(
                text=SINON_BASICC,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, SINON_BASIC, "sinonbasic")
                ),
            )

        elif back_match:
            query.message.edit_text(
                text=SINON_BASICC,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, SINON_BASIC, "sinonbasic")
                ),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()

    except BadRequest:
        pass


def sinon_about_callback(update, context):
    query = update.callback_query
    if query.data == "sinon_":
        query.message.edit_text(
               text=SINON,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="❓ How To Use Me", callback_data="sinon_howto"
                        ),
                        InlineKeyboardButton(
                            text="⚠️ T.A.C", callback_data="sinon_tac"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="🔐 Help", callback_data="help_back"
                        )
                    ],
                    [InlineKeyboardButton(text="Back", callback_data="sinon_back")]
                ]
            ),
        )
    elif query.data == "sinon_back":
        first_name = update.effective_user.first_name
        uptime = get_readable_time((time.time() - StartTime))
        query.message.edit_text(
                PM_START_TEXT.format(
                    escape_markdown(first_name),
                    escape_markdown(uptime),
                    sql.num_users(),
                    sql.num_chats()),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
                disable_web_page_preview=False,
        )

    elif query.data == "sinon_basichelp":
        query.message.edit_text(
            text=SINO_BASIC,           
        parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(SINO_CMDS),
        )
    
    elif query.data == "sinon_notes":
        query.message.edit_text(
            text="""<b> ♡ Setting Up Notes </b>"
♡ can save message/media/audio or anything as notes
♡ To get a note simply use # at the beginning of a word
♡ You can also set buttons for notes and filters (refer help menu)""",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Back", callback_data="sinon_basichelp")]]
            ),
        )
    elif query.data == "sinon_admin":
        query.message.edit_text(
            text=SINON_ADMIN,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Back", callback_data="sinon_basichelp")]]
            ),
        )    
    elif query.data == "sinon_support":
        query.message.edit_text(
            text="""*♡ Sinon Support Chats*
♡ Join Support Group/Channel""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="🚑 Network", url="t.me/YatoNetwork"),
                 ],
                 [
                    InlineKeyboardButton(text="🗯️ Support", url="t.me/SinonSupport"),
                    InlineKeyboardButton(text="🔔 Updates", url="t.me/SinonUpdates"),
                 ],
                 [
                    InlineKeyboardButton(text="Back", callback_data="sinon_basichelp"),
                 
                 ]
                ]
            ),
        )
    elif query.data == "sinon_credit":
        query.message.edit_text(
            text="""<b> ♡ Credits Of Sinon </b>
♡ Here Some Developers Helping In Making Of Sinon""",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="Alone X", url="t.me/ItzAloneX"),
                 ],
                 [
                    InlineKeyboardButton(text="Back", callback_data="sinon_basichelp"),
                 
                 ]
                ]
            ),
        )

    elif query.data == "sinon_howto":
        query.message.edit_text(
            text=HOWTOUSE,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="👷🏻‍♂️ Admins Settings", callback_data="sinon_permis"),                        
                    InlineKeyboardButton(text="💬 Anti Spam", callback_data="sinon_spamprot"),                      
                 ],
                 [
                    InlineKeyboardButton(text="🎸 Music Setup", callback_data="sinon_cbguide"),                        
                 ],
                 [
                    InlineKeyboardButton(text="Back", callback_data="sinon_back"),
                 ]
                ]
            ),
        )
    elif query.data == "sinon_permis":
        query.message.edit_text(
            text="""<b> ♡ Admin Permissions</b>

To avoid slowing down, Sinon caches admin rights for each user. This cache lasts about 10 minutes; this may change in the future. This means that if you promote a user manually (without using the /promote command), Sinon will only find out ~10 minutes later.
If you want to update them immediately, you can use the /admincache command,thta'll force Sinon to check who the admins are again and their permissions
If you are getting a message saying:

You must be this chat administrator to perform this action!

This has nothing to do with Sinon rights; this is all about your permissions as an admin. Sinon respects admin permissions; if you do not have the Ban Users permission as a telegram admin, you won't be able to ban users with Sinon. Similarly, to change Sinon settings, you need to have the Change group info permission.
The message very clearly says that you need these rights not Sinon""",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Back", callback_data="sinon_howto")]]
            ),
        )
    elif query.data == "sinon_spamprot":
        query.message.edit_text(
            text="""*♡  Anti-Spam Settings*

/antispam <on/off/yes/no>: Change antispam security settings in the group, or return your current settings(when no arguments).
_This helps protect you and your groups by removing spam flooders as quickly as possible._

♡ /setflood <int/'no'/'off'>: enables or disables flood control
♡ /setfloodmode <ban/kick/mute/tban/tmute> <value>: Action to perform when user have exceeded flood limit. ban/kick/mute/tmute/tban

_Antiflood allows you to take action on users that send more than x messages in a row. Exceeding the set flood will result in restricting that user._
♡ /addblacklist <triggers>: Add a trigger to the blacklist. Each line is considered one trigger, so using different lines will allow you to add multiple triggers.
♡ /blacklistmode <off/del/warn/ban/kick/mute/tban/tmute>: Action to perform when someone sends blacklisted words.

_Blacklists are used to stop certain triggers from being said in a group. Any time the trigger is mentioned, the message will immediately be deleted. A good combo is sometimes to pair this up with warn filters!_
 ♡ /reports <on/off>: Change report setting, or view current status.
 ♡ If done in pm, toggles your status.
 ♡ If in chat, toggles that chat's status.

_If someone in your group thinks someone needs reporting, they now have an easy way to call all admins._
♡ /lock <type>: Lock items of a certain type (not available in private)
♡ /locktypes: Lists all possible locktypes

_The locks module allows you to lock away some common items in the telegram world; the bot will automatically delete them!_
♡ /addwarn <keyword> <reply message>: Sets a warning filter on a certain keyword. If you want your keyword to be a sentence, encompass it with quotes, as such: /addwarn "very angry" This is an angry user. 
♡ /warn <userhandle>: Warns a user. After 3 warns, the user will be banned from the group. Can also be used as a reply.
♡ /strongwarn <on/yes/off/no>: If set to on, exceeding the warn limit will result in a ban. Else, will just kick.

_If you're looking for a way to automatically warn users when they say certain things, use the /addwarn command._
♡ /welcomemute <off/soft/strong>: All users that join, get muted

_ A button gets added to the welcome message for them to unmute themselves. This proves they aren't a bot! soft - restricts users ability to post media for 24 hours. strong - mutes on join until they prove they're not bots._""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Back", callback_data="sinon_howto")]]
            ),
        )
    elif query.data == "sinon_tac":
        query.message.edit_text(
            text="""<b> ♡ Terms and Conditions </b>
__To Use This Bot, You Need To Read Terms and Conditions Carefully.__
♡ We always respect your privacy We never log into bot's api and spying on you We use a encripted database Bot will automatically stops if someone logged in with api.
♡ Always try to keep credits, so This hardwork is done by @ItzAloneX spending many sleepless nights.. So, Respect it.
♡ Some modules in this bot is owned by different authors, So, All credits goes to them.
♡ If you need to ask anything about this bot, Come @SinonSupport.
♡ If you asking nonsense in Support Chat, you will get warned/banned.
♡ All api's we used owned by originnal authors Some api's we use Free version Please don't overuse AI Chat.
For any kind of help, related to this bot, Join @SinonSupport.
__Terms & Conditions will be changed anytime__""",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="Back", callback_data="sinon_howto"),
                    ]
                ]
            ),
        )
    elif query.data == "sinon_cbguide":
        query.message.edit_text(
            text="""*♡ How To Setup Music*
1. **First, add me to your group.
2. **Then promote me as admin and give all permissions except anonymous admin.
3. **After promoting me, type /admincache in group to update the admin list.
4. **Add @SinonAssistant to your group.
5. **Turn on the video chat first before start to play music.
📌 **If the userbot not joined to video chat, make sure if the video chat already turned on, or you can ask Admins in @SinonSupport.**
💫 __Powered by Sinon A.I__""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🔺", callback_data="sinon_cbhelps"
                        ),
                        InlineKeyboardButton(text="Back", callback_data="sinon_howto"),
                        InlineKeyboardButton(
                            text="🔻", callback_data="sinon_cbhelps"
                        ),
                    ]
                ]
            ),
        )
    elif query.data == "sinon_cbhelps":
        query.message.edit_text(
            text="""* ♡ Music Commands *
1. **/play (name song) for playing music.
2. **/pause for paused music.
3. **/resume for resume music.
4. **/stop or /end for end music playing.
5. **/music (name song) for download song.
6. **/video (name video) for download video.
7. **/lyrics for searching lyrics.
📌 **Also you can download music or video with push button menu.**
💫 __Powered by Sinon A.I__""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🔺", callback_data="sinon_cbguide"
                        ),
                        InlineKeyboardButton(text="Back", callback_data="sinon_howto"),
                        InlineKeyboardButton(
                            text="🔻", callback_data="sinon_cbguide"
                        ),
                    ]
                ]
            ),
        )        

def Source_about_callback(update, context):
    query = update.callback_query
    if query.data == "source_":
        query.message.edit_text(
            text="""*♡ Sinon Is The Redisigned Version Of Open Source Projects.*
                    \n*♡ Sinon Source Code Was Rewritten By @ItzAloneX And All Of Conrtibutor For Help Sinon.*
                    \n*♡ If Any Question About Sinon,Let Us Know At @SinonSupport.*
                 """,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="Go Back", callback_data="source_back")
                 ]
                ]
            ),
        )
    elif query.data == "source_back":
        query.message.edit_text(
                PM_START_TEXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
                disable_web_page_preview=False,
        )


def get_help(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_text(
                f"Contact me in PM to get help of {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="🔐 Help",
                                url="t.me/{}?start=ghelp_{}".format(
                                    context.bot.username, module
                                ),
                            )
                        ]
                    ]
                ),
            )
            return
        update.effective_message.reply_text(
            "Contact me in PM to get the list of possible commands.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🔐 Help​",
                            url="t.me/{}?start=help".format(context.bot.username),
                        )
                    ]
                ]
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "Here is the available help for the *{}* module:\n".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].__help__
        )
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Go Back​", callback_data="help_back")]]
            ),
        )

    else:
        send_help(chat.id, HELP_STRINGS)


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                "These are your current settings:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text="Which module would you like to check {}'s settings for?".format(
                    chat_name
                ),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any chat settings available :'(\nSend this "
                "in a group chat you're admin in to find its current settings!",
                parse_mode=ParseMode.MARKDOWN,
            )


def settings_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* has the following settings for the *{}* module:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Go Back​",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                text="Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            "Message is not modified",
            "Query_id_invalid",
            "Message can't be deleted",
        ]:
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))


def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "Click here to get this chat's settings, as well as yours."
            msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Settings",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id
                                ),
                            )
                        ]
                    ]
                ),
            )
        else:
            text = "Click here to check your settings."

    else:
        send_settings(chat.id, user.id, True)


def donate(update: Update, context: CallbackContext):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]
    bot = context.bot
    if chat.type == "private":
        update.effective_message.reply_text(
            DONATE_STRING, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
        )

        if OWNER_ID != 5259108841:
            update.effective_message.reply_text(
                "I'm free for everyone ❤️ If you wanna make me smile, just join"
                "[My Channel]({})".format(DONATION_LINK),
                parse_mode=ParseMode.MARKDOWN,
            )
    else:
        try:
            bot.send_message(
                user.id,
                DONATE_STRING,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )

            update.effective_message.reply_text(
                "I've PM'ed you about donating to my creator!"
            )
        except Unauthorized:
            update.effective_message.reply_text(
                "Contact me in PM first to get donation information."
            )


def migrate_chats(update: Update, context: CallbackContext):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Successfully migrated!")
    raise DispatcherHandlerStop


def main():

    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.sendMessage(
                f"@{SUPPORT_CHAT}",
                f"""**[Sinon 詩乃 Started!](https://telegra.ph/file/84613a50050e3991f404b.jpg)**""",
                parse_mode=ParseMode.MARKDOWN,
            )
        except Unauthorized:
            LOGGER.warning(
                "Bot isnt able to send message to support_chat, go and check!"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)

    test_handler = CommandHandler("test", test, run_async=True)
    start_handler = CommandHandler("start", start, run_async=True)

    help_handler = CommandHandler("help", get_help, run_async=True)
    help_callback_handler = CallbackQueryHandler(
        help_button, pattern=r"help_.*", run_async=True
    )

    settings_handler = CommandHandler("settings", get_settings, run_async=True)
    settings_callback_handler = CallbackQueryHandler(
        settings_button, pattern=r"stngs_", run_async=True
    )

    sinon_callback_handler = CallbackQueryHandler(
        sinon_about_callback, pattern=r"sinon_", run_async=True
    )

    source_callback_handler = CallbackQueryHandler(
        Source_about_callback, pattern=r"source_", run_async=True
    )

    donate_handler = CommandHandler("donate", donate, run_async=True)
    migrate_handler = MessageHandler(
        Filters.status_update.migrate, migrate_chats, run_async=True
    )

    dispatcher.add_handler(test_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(source_callback_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(sinon_callback_handler)
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)
    dispatcher.add_handler(donate_handler)

    dispatcher.add_error_handler(error_callback)

    if WEBHOOK:
        LOGGER.info("Using webhooks.")
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)

        if CERT_PATH:
            updater.bot.set_webhook(url=URL + TOKEN, certificate=open(CERT_PATH, "rb"))
        else:
            updater.bot.set_webhook(url=URL + TOKEN)

    else:
        LOGGER.info("Using long polling.")
        updater.start_polling(timeout=15, read_latency=4, drop_pending_updates=True)

    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()

    updater.idle()


if __name__ == "__main__":
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    telethn.start(bot_token=TOKEN)
    pbot.start()
    main()
