import logging
from pyrogram import Client, filters, StopPropagation
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import Config, Txt

log = logging.getLogger(__name__)

@Client.on_message(filters.private & filters.command("help"), group=-2)
async def core_help(_, message):
    text = (
        "<b>ANIFLIX AUTO RENAME BOT — HELP</b>\n\n"
        "<b>Rename</b>\n"
        "/autorename — Set filename format\n"
        "Send a video/document after setting the format.\n\n"
        "<b>Caption</b>\n/set_caption — Set caption\n/see_caption — View caption\n/del_caption — Delete caption\n\n"
        "<b>Thumbnail</b>\n/setthumb — Start thumbnail setup\n/viewthumb — View thumbnail\n/delthumb — Delete thumbnail\n\n"
        "<b>Metadata</b>\n/metadata — Metadata settings\n\n"
        "Use /tutorial for steps or /about for bot information.\n"
        "Support: @TANJIROKAMADO404"
    )
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup([[
        InlineKeyboardButton("Tutorial", callback_data="core_tutorial"),
        InlineKeyboardButton("About", callback_data="core_about"),
    ]]), disable_web_page_preview=True)
    raise StopPropagation

@Client.on_message(filters.private & filters.command("tutorial"), group=-2)
async def core_tutorial(_, message):
    await message.reply_text(
        "<b>QUICK TUTORIAL</b>\n\n"
        "1. Send /autorename and choose a filename format.\n"
        "2. Send a video or document to rename it.\n"
        "3. Use /set_caption to configure a caption.\n"
        "4. Use /setthumb, then send a photo to save a thumbnail.\n"
        "5. Use /metadata to configure media metadata.\n\n"
        "For help, contact @TANJIROKAMADO404.",
        disable_web_page_preview=True,
    )
    raise StopPropagation

@Client.on_message(filters.private & filters.command("about"), group=-2)
async def core_about(_, message):
    try:
        await message.reply_text(Txt.ABOUT_TXT, disable_web_page_preview=True)
    except Exception:
        log.exception("Configured ABOUT_TXT failed; sending fallback")
        await message.reply_text(
            "<b>ANIFLIX Auto Rename & Encoder Bot</b>\n"
            "Pyrogram 2.0\nPowered by @ANIFLIXANIMETAMIL\n"
            "Developer: @TANJIROKAMADO404",
            disable_web_page_preview=True,
        )
    raise StopPropagation
