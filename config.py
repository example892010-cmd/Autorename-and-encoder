import re, os, time
id_pattern = re.compile(r'^.\d+$') 

class Config(object):
    # pyro client config
    API_ID    = int(os.environ.get("API_ID", "0") or "0")
    API_HASH  = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "") 

    # database config
    DB_NAME = os.environ.get("DB_NAME", "autorename")     
    DB_URL  = os.environ.get("DB_URL","")
 
    # other configs
    BOT_UPTIME  = time.time()
    START_PIC   = os.environ.get("START_PIC", "")
    ADMIN = []
    for admin in re.split(r"[\s,]+", os.environ.get("ADMIN", "").strip()):
        if admin:
            try:
                ADMIN.append(int(admin))
            except ValueError:
                ADMIN.append(admin.lstrip("@"))
    # -- FORCE_SUB_CHANNELS = ["BotzPW","AshuSupport","AshutoshGoswami24"] -- # 
    FORCE_SUB_CHANNELS = [
        x.strip().lstrip('@') for x in (
            os.environ.get('FORCE_SUB_CHANNELS') or os.environ.get('FORCE_SUB') or ''
        ).split(',') if x.strip()
    ]
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0") or "0")
    PORT = int(os.environ.get("PORT", "10000") or "10000")
    ENCODE_RESOLUTIONS = os.environ.get("ENCODE_RESOLUTIONS", "480,720,1080")
    
    # wes response configuration     
    WEBHOOK = os.environ.get("WEBHOOK", "True").strip().lower() in {"1", "true", "yes", "on"}



class Txt(object):
    START_TXT = """👋 Hello {}!

➻ Advanced Auto Rename Bot
➻ Custom Thumbnail & Caption
➻ Use /tutorial To Get Started

⚡ Powered By @ANIFLIXANIMETAMIL
👨‍💻 Developer: @TANJIROKAMADO404
"""

    FILE_NAME_TXT = """<b><u>SETUP AUTO RENAME FORMAT</u></b>

Use These Keywords To Setup Custom File Name

✓ `{{title}}` :- Anime / Movie title
✓ `{{season}}` :- Season number
✓ `{{episode}}` :- Episode number
✓ `{{quality}}` :- Video resolution

<b>➻ Example :</b> <code>/autorename {{title}} S{{season}} Ep{{episode}} [{{quality}}] [TAMIL]</code>

<b>➻ Your Current Auto Rename Format :</b> <code>{format_template}</code>"""

    ABOUT_TXT = """<b>🤖 My Name :</b> ANIFLIX RENAME BOT ⚡
<b>📝 Language :</b> Python 3
<b>📚 Library :</b> Pyrogram 2.0
<b>🚀 Server :</b> Railway
<b>📢 Channel :</b> @ANIFLIXANIMETAMIL
<b>🧑‍💻 Developer :</b> @TANJIROKAMADO404

<b>♻️ Bot Made By :</b> @TANJIROKAMADO404"""

    SEND_METADATA = "<b>Send the metadata text you want to use.</b>"

    META_TXT = """<b>㊋ HOW TO SET METADATA</b>

Use these commands to set individual media metadata:

/settitle — Set title
/setauthor — Set author
/setartist — Set artist
/setaudio — Set audio title
/setsubtitle — Set subtitle title
/setvideo — Set video title

Use /metadata to turn metadata On or Off."""

    THUMBNAIL_TXT = """<b><u>🖼️ HOW TO SET THUMBNAIL</u></b>

⦿ Send a photo to the bot to set your custom thumbnail.
⦿ /viewthumb - View your thumbnail
⦿ /delthumb - Delete your thumbnail"""

    CAPTION_TXT = """<b><u>📝 HOW TO SET CAPTION</u></b>

⦿ /set_caption - Set your caption
⦿ /see_caption - View your caption
⦿ /del_caption - Delete your caption"""

    PROGRESS_BAR = """<b>
╭━━━━❰ᴘʀᴏɢʀᴇss ʙᴀʀ❱━➣
┣⪼ 🗃️ Sɪᴢᴇ: {1} | {2}
┣⪼ ⏳️ Dᴏɴᴇ : {0}%
┣⪼ 🚀 Sᴩᴇᴇᴅ: {3}/s
┣⪼ ⏰️ Eᴛᴀ: {4}
╰━━━━━━━━━━━━━━━➣ </b>"""

    DONATE_TXT = """<b>💬 Need Help?</b>

For any issues with the bot, contact the developer.

<b>🧑‍💻 Developer:</b> @TANJIROKAMADO404
<b>📢 Updates:</b> https://t.me/+1CcAFHLS2tU4YWVl
<b>💬 Support:</b> https://t.me/+1jDuhUQ41hA1YmVl"""

    HELP_TXT = """<b>Hey</b> {} 👋

Use the buttons below to configure your Auto Rename Bot.

⚠️ For any issues, contact @TANJIROKAMADO404"""
