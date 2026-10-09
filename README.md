## Auto Rename Bot With Metadata Rename


##  Configurations

- `BOT_TOKEN` - Get the bot token from [@BotFather](https://t.me/BotFather).
- `API_ID` - Obtain from [my.telegram.org](https://my.telegram.org).
- `API_HASH` - Obtain from [my.telegram.org](https://my.telegram.org).
- `ADMIN` - Bot controllers' IDs, use space to split multiple IDs.
- `LOG_CHANNEL` - Bot log sending channel. **Note:** ID must start with `-100`.
- `DB_URL` - MongoDB URL from [MongoDB Atlas](https://cloud.mongodb.com).
- `DB_NAME` - Your MongoDB database name. **Optional**.
- `FORCE_SUB_CHANNELS` - Your force subscription channel usernames without `@`. **Optional**. Use format `1CHANNEL,2CHANNEL`.
- `START_PIC` - Start message photo. **Optional**.
- `WEBHOOK` - Set to `True` if your server requires web services, otherwise set to `False`. **Optional**.

## Deploy to Koyeb

<a target="_blank" href="https://app.koyeb.com/deploy?type=git&repository=github.com/AshutoshGoswami24/Auto-Rename-Bot&branch=main&name=ashu-rename-bot">
  <img src="https://www.koyeb.com/static/images/deploy/button.svg" alt="Deploy to Koyeb" style="width:170px;">
</a>

## Deploy to Heroku

<a href="https://heroku.com/deploy?template=https://github.com/AshutoshGoswami24/Auto-Rename-Bot">
  <img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy to Heroku" style="width:170px;">
</a>

## Deploy to Cloud Shell Editor

<a target="_blank" href="https://shell.cloud.google.com/cloudshell/open?cloudshell_git_repo=https://github.com/AshutoshGoswami24/Auto-Rename-Bot&tutorial=Ashu/g-cloud.md">
  <img src="https://raw.githubusercontent.com/AshutoshGoswami24/text-leech-bot/main/.github/img/x.svg" alt="Deploy to Cloud Shell Editor" style="width:170px;">
</a>

## 🥰 Features

- Renames files very fast.
- Permanent thumbnail support.
- Force join for the user to use the bot.
- Supports broadcasts.
- Custom caption support.
- Custom start-up picture.
- Force subscription available.
- Supports unlimited renaming at a time.
- Deploy to Koyeb, Heroku, and Railway.
- Automatically rename your files.
- Set media type to upload file type.
- METADATA add with rename.

### 🚦 User Commands

```
start - Check if the bot is running.
autorename - To auto rename your files.
tutorial - SETUP AUTO RENAME FORMAT 
setmedia - To set your media type preference.
metadata - to set metadata
viewthumb - To view current thumbnail.
delthumb - To delete current thumbnail.
set_caption - set a custom caption.
see_caption - see your custom caption.
del_caption - delete custom caption.
restart - To restart the bot [FOR ADMINS USE ONLY]
broadcast - Message Broadcast command [FOR ADMINS USE ONLY].
status - Check bot status [FOR ADMINS USE ONLY].
```

## Connect with Me

<p align="center">
<a href="https://t.me/AshutoshGoswami24">
  <img src="https://img.shields.io/badge/-Asʜᴜᴛᴏsʜ Gᴏsᴡᴀᴍɪ 𝟸𝟺 🇮🇳™-0077B5?style=flat&logo=Telegram&logoColor=white"/>
</a>
<a href="https://t.me/AshuSupport">
  <img src="https://img.shields.io/badge/-Ashu Support-0077B5?style=flat&logo=Telegram&logoColor=white"/>
</a>
</p>

---

Credits: 🎖️ [𝗔𝘀𝗵𝘂𝘁𝗼𝘀𝗵𝗚𝗼𝘀𝘄𝗮𝗺𝗶𝟮𝟰](https://github.com/AshutoshGoswami24) 🤖

_Last Edited on: 08/21/2024, 10:12:42 AM_


## Automatic multi-resolution encoding

Video uploads (including common video files sent as documents) are automatically encoded to 480p, 720p, and 1080p. Each result uses the user's `/autorename` format and is uploaded as soon as that resolution finishes; the bot does not wait for the other outputs before uploading a completed one. Existing caption and custom-thumbnail settings are applied to each encoded result. Non-video documents and audio continue through the existing rename handler. FFmpeg is installed in the Docker image used by the included Render Blueprint.

Environment options: `ENCODE_RESOLUTIONS` (comma-separated heights), `ENCODE_CONCURRENCY` (default 2), `ENCODE_PRESET` (default `veryfast`), and `ENCODE_CRF` (default 24). Encoding is CPU-intensive; small free instances may take a long time or run out of memory on large source videos.

## Automatic multi-resolution encoding

Video uploads (including common video files sent as documents) are automatically encoded to 480p, 720p, and 1080p. Each result uses the user's `/autorename` template and uploads as soon as its encode finishes. Existing custom captions, thumbnails, and configured metadata are applied to each encoded result. Non-video documents and audio continue through the original rename handler. FFmpeg is installed in the Docker image used by the included Render Blueprint.

Environment options: `ENCODE_RESOLUTIONS` (comma-separated heights), `ENCODE_CONCURRENCY` (default 2), `ENCODE_PRESET` (default `veryfast`), and `ENCODE_CRF` (default 24). Encoding is CPU-intensive; small free instances may take a long time or run out of memory on large source videos.


## Important deployment checks

- Set `API_ID`, `API_HASH`, `BOT_TOKEN`, `ADMIN`, and a valid MongoDB `DB_URL` in Render Environment.
- Set `DB_NAME=autorename` if that is the database name in your MongoDB cluster.
- `LOG_CHANNEL` is optional; leave it empty or set it to `0` if startup notifications are not needed.
- The bot supports `/start`, `/help`, `/about`, `/tutorial`, `/ping`, `/autorename`, `/setmedia`, `/set_caption`, `/del_caption`, `/see_caption`, `/setthumb`, `/viewthumb`, `/delthumb`, `/metadata`, `/settitle`, `/setauthor`, `/setartist`, `/setaudio`, `/setsubtitle`, `/setvideo`, `/stats`, `/broadcast` (reply to a message), and admin-only `/restart`.
- Sending a photo saves it as the custom thumbnail.
- A missing `DB_URL` no longer prevents the non-database commands from loading; database-dependent commands will tell you to configure it.
