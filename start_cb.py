import os
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ForceReply,
    CallbackQuery,
    Message,
    InputMediaPhoto,
)

from helper.database import AshutoshGoswami24
from config import Config, Txt


async def _edit_menu_message(message, **kwargs):
    """Edit text menus correctly whether /start was sent with a photo or text."""
    text = kwargs.get("text", "")
    markup = kwargs.get("reply_markup")
    if getattr(message, "photo", None) or getattr(message, "video", None) or getattr(message, "document", None):
        return await message.edit_caption(caption=text, reply_markup=markup)
    return await message.edit_text(
        text=text,
        reply_markup=markup,
        disable_web_page_preview=kwargs.get("disable_web_page_preview", False),
    )


@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):
    user = message.from_user
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📢 Updates", url="https://t.me/+1CcAFHLS2tU4YWVl"),
                InlineKeyboardButton("💬 Support", url="https://t.me/+1jDuhUQ41hA1YmVl"),
            ],
            [
                InlineKeyboardButton("⚙️ Help", callback_data="help"),
                InlineKeyboardButton("💙 About", callback_data="about"),
            ],
            [
                InlineKeyboardButton("🧑‍💻 Developer", url="https://t.me/TANJIROKAMADO404")
            ],
        ]
    )

    # Reply first so a database/log-channel problem cannot block /start.
    local_start_pic = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "helper", "start_pic.jpg"
    )
    start_pic = Config.START_PIC
    try:
        if start_pic and not start_pic.startswith(
            ("https://t.me/", "http://t.me/", "https://telegram.me/", "http://telegram.me/")
        ):
            await message.reply_photo(
                start_pic, caption=Txt.START_TXT.format(user.first_name),
                reply_markup=button,
            )
        elif os.path.exists(local_start_pic):
            await message.reply_photo(
                local_start_pic, caption=Txt.START_TXT.format(user.first_name),
                reply_markup=button,
            )
        else:
            await message.reply_text(
                Txt.START_TXT.format(user.first_name), reply_markup=button,
                disable_web_page_preview=True,
            )
    except Exception:
        import logging
        logging.exception("Start photo failed; falling back to text")
        try:
            await message.reply_text(
                Txt.START_TXT.format(user.first_name), reply_markup=button,
                disable_web_page_preview=True,
            )
        except Exception:
            logging.exception("Failed to send /start text reply")
            return

    # Keep user tracking and optional log notifications, but never let them block the reply.
    try:
        await AshutoshGoswami24.add_user(client, message)
    except Exception:
        import logging
        logging.exception("Could not save user after /start")

    if Config.LOG_CHANNEL:
        try:
            username = f"@{user.username}" if user.username else "No username"
            await client.send_message(
                Config.LOG_CHANNEL,
                f"🚀 **{user.first_name} started the bot**\n\n"
                f"👤 Name: {user.first_name}\n"
                f"🆔 ID: `{user.id}`\n"
                f"🔗 Username: {username}",
            )
        except Exception:
            import logging
            logging.exception("Could not send /start log")


@Client.on_callback_query(filters.regex(r"^(home|caption|help|donate|file_names|thumbnail|about|close|core_tutorial|core_about)$"))
async def cb_handler(client, query: CallbackQuery):
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data == "core_tutorial":
        await _edit_menu_message(
            query.message,
            text=(
                "<b>QUICK TUTORIAL</b>\n\n"
                "1. Use /autorename followed by your filename format.\n"
                "2. Send a video or video document to encode, or another file to rename.\n"
                "3. Use /set_caption to set an upload caption.\n"
                "4. Use /setthumb, then send a photo to save a thumbnail.\n"
                "5. Use /metadata to configure media metadata.\n\n"
                "Help: @TANJIROKAMADO404"
            ),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="home")]]),
        )
        return
    if data == "core_about":
        await _edit_menu_message(
            query.message,
            text=Txt.ABOUT_TXT,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="home")]]),
            disable_web_page_preview=True,
        )
        return

    if data == "home":
        await _edit_menu_message(query.message, 
            text=Txt.START_TXT.format(query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("📢 Updates", url="https://t.me/+1CcAFHLS2tU4YWVl"),
                        InlineKeyboardButton(
                            "💬 Support", url="https://t.me/+1jDuhUQ41hA1YmVl"
                        ),
                    ],
                    [
                        InlineKeyboardButton("⚙️ Help", callback_data="help"),
                        InlineKeyboardButton("💙 About", callback_data="about"),
                    ],
                    [
                        InlineKeyboardButton(
                            "🧑‍💻 Developer 🧑‍💻", url="https://t.me/TANJIROKAMADO404"
                        )
                    ],
                ]
            ),
        )
    elif data == "caption":
        await _edit_menu_message(query.message, 
            text=Txt.CAPTION_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("✖️ Close", callback_data="close"),
                        InlineKeyboardButton("🔙 Back", callback_data="help"),
                    ]
                ]
            ),
        )
    elif data == "help":
        await _edit_menu_message(query.message, 
            text=Txt.HELP_TXT.format(client.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⚙️ Setup AutoRename Format ⚙️", callback_data="file_names"
                        )
                    ],
                    [
                        InlineKeyboardButton("🖼️ Thumbnail", callback_data="thumbnail"),
                        InlineKeyboardButton("✏️ Caption", callback_data="caption"),
                    ],
                    [
                        InlineKeyboardButton("🏠 Home", callback_data="home"),
                        InlineKeyboardButton("💰 Donate", callback_data="donate"),
                    ],
                ]
            ),
        )
    elif data == "donate":
        await _edit_menu_message(query.message, 
            text=Txt.DONATE_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("✖️ Close", callback_data="close"),
                        InlineKeyboardButton("🔙 Back", callback_data="help"),
                    ]
                ]
            ),
        )

    elif data == "file_names":
        format_template = await AshutoshGoswami24.get_format_template(user_id)
        await _edit_menu_message(query.message, 
            text=Txt.FILE_NAME_TXT.format(format_template=format_template),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("✖️ Close", callback_data="close"),
                        InlineKeyboardButton("🔙 Back", callback_data="help"),
                    ]
                ]
            ),
        )

    elif data == "thumbnail":
        await _edit_menu_message(query.message, 
            text=Txt.THUMBNAIL_TXT,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("✖️ Close", callback_data="close"),
                        InlineKeyboardButton("🔙 Back", callback_data="help"),
                    ]
                ]
            ),
        )

    elif data == "about":
        await _edit_menu_message(query.message, 
            text=Txt.ABOUT_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("✖️ Close", callback_data="close"),
                        InlineKeyboardButton("🔙 Back", callback_data="home"),
                    ]
                ]
            ),
        )

    elif data == "close":
        try:
            await query.message.delete()
        except Exception:
            pass
        return
