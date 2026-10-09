import asyncio
import logging
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
logging.getLogger("pyrogram").setLevel(logging.ERROR)


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
