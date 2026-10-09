ANIFLIX Auto Rename Bot — targeted startup/plugin discovery fix

Included file: bot.py only.

Copy this file to the root of your existing repository, replacing the old bot.py.
Keep the plugins/ directory and all existing environment variables unchanged.

This update anchors the working directory to bot.py, performs explicit preflight
imports for all nine expected plugins, logs full tracebacks for import failures,
and increases Pyrogram logging so plugin discovery problems are visible in Render.

After deployment, check for lines beginning with:
  Plugin import preflight OK:
  PLUGIN IMPORT FAILED:
  Registered Pyrogram handler counts by group:

Do not share BOT_TOKEN, API_HASH, or DB_URL in logs/screenshots.
