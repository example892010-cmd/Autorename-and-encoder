import asyncio
import logging
from datetime import datetime

from aiohttp import web
from pyrogram import Client, __version__, filters
from pyrogram.raw.all import layer
from pyrogram.handlers import MessageHandler
from pytz import timezone

from config import Config
from route import web_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logging.getLogger("pyrogram").setLevel(logging.INFO)


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="ANIFLIX_RENAME_BOT",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=200,
            plugins={"root": "plugins"},
            sleep_threshold=15,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username

        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", Config.PORT).start()

        # Diagnostics: prove whether Telegram updates reach this process.
        async def trace_private_update(client, message):
            text = (message.text or message.caption or "<non-text message>")[:100]
            logging.info(
                "Incoming private update from user_id=%s: %s",
                getattr(message.from_user, "id", "unknown"),
                text,
            )

        # Fallback handlers are added after plugin loading. If the normal plugin
        # command is registered, it runs first in group 0; otherwise these reply.
        async def fallback_start(client, message):
            logging.warning("Fallback /start handler was used; inspect plugin loading.")
            try:
                await message.reply_text(
                    "👋 Hello " + (message.from_user.first_name or "there") + "!\n\n"
                    "Advanced Auto Rename Bot\n"
                    "Use /help or /tutorial to get started.\n\n"
                    "Powered By @ANIFLIXANIMETAMIL\n"
                    "Developer: @TANJIROKAMADO404"
                )
            except Exception:
                logging.exception("Fallback /start reply failed")

        async def fallback_ping(client, message):
            logging.warning("Fallback /ping handler was used; inspect plugin loading.")
            try:
                await message.reply_text("Pong! The bot is receiving commands.")
            except Exception:
                logging.exception("Fallback /ping reply failed")

        self.add_handler(
            MessageHandler(trace_private_update, filters.private),
            group=-100,
        )
        self.add_handler(
            MessageHandler(fallback_start, filters.private & filters.command("start")),
            group=0,
        )
        self.add_handler(
            MessageHandler(fallback_ping, filters.private & filters.command(["ping", "p"])),
            group=0,
        )

        logging.info(
            "%s started successfully | Pyrogram %s | Layer %s",
            me.first_name,
            __version__,
            layer,
        )

        for admin in Config.ADMIN:
            try:
                await self.send_message(
                    admin,
                    f"**{me.first_name} started successfully.**",
                )
            except Exception:
                logging.exception("Could not notify admin %s", admin)

        if Config.LOG_CHANNEL:
            try:
                now = datetime.now(timezone("Asia/Kolkata"))
                await self.send_message(
                    Config.LOG_CHANNEL,
                    f"**{me.mention} restarted successfully!**\n\n"
                    f"📅 Date: `{now.strftime('%d %B, %Y')}`\n"
                    f"⏰ Time: `{now.strftime('%I:%M:%S %p')}`\n"
                    f"🌐 Timezone: `Asia/Kolkata`\n"
                    f"🤖 Version: `v{__version__} (Layer {layer})`",
                )
            except Exception:
                logging.exception("Could not send startup log")

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped.")


async def main():
    bot = Bot()
    await bot.start()
    try:
        await asyncio.Event().wait()
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
