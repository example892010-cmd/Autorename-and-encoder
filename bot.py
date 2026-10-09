import asyncio
import importlib
import logging
import os
import sys
from datetime import datetime

from aiohttp import web
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from pytz import timezone

from config import Config
from route import web_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logging.getLogger("pyrogram").setLevel(logging.DEBUG)
logging.getLogger("pyrogram.dispatcher").setLevel(logging.DEBUG)

# Render may launch the start command from a different working directory.
# Anchor imports and Pyrogram's plugin discovery to this file's directory.
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_DIR)
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

PLUGIN_MODULES = (
    "plugins.admin_panel",
    "plugins.auto_rename",
    "plugins.core_commands",
    "plugins.encode_pipeline",
    "plugins.file_rename",
    "plugins.force_subs",
    "plugins.metadata",
    "plugins.start_cb",
    "plugins.thumb_cap",
)

# Preflight imports so Pyrogram cannot silently leave the bot online with zero
# handlers. Importing a module is safe here; Pyrogram still discovers its
# decorated handlers from the same module package during Client startup.
for _module_name in PLUGIN_MODULES:
    try:
        importlib.import_module(_module_name)
        logging.info("Plugin import preflight OK: %s", _module_name)
    except Exception:
        logging.exception("PLUGIN IMPORT FAILED: %s", _module_name)


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="ANIFLIX_RENAME_BOT",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=32,
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

        handler_counts = {group: len(handlers) for group, handlers in self.dispatcher.groups.items()}
        total_handlers = sum(handler_counts.values())
        logging.info("Registered Pyrogram handler counts by group: %s", handler_counts)
        if total_handlers == 0:
            logging.critical(
                "ZERO HANDLERS REGISTERED. Check the preceding PLUGIN IMPORT FAILED "
                "tracebacks and confirm the repository root contains plugins/*.py."
            )
        elif total_handlers < 10:
            logging.warning("Only %s handlers registered; inspect plugin import warnings.", total_handlers)

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
