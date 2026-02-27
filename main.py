import sys
import logging

import discord
from config import settings
from bot import MovieNightBot

discord.utils.setup_logging(root=True, level=settings.get("LOG_LEVEL"))
logger = logging.getLogger(__name__)

token = settings.get("APP_TOKEN")
guild_id = settings.get("GUILD_ID")
if not token:
    logger.error("APP_TOKEN is not set. Add it to your .env file or environment.")
    sys.exit()
if guild_id:
    logger.info("Guild ID: %s", guild_id)
    guild_id = discord.Object(guild_id)
intents = discord.Intents.default()
intents.message_content = True

bot = MovieNightBot(guild_id=guild_id, command_prefix='/', intents=intents)

bot.run(token, log_handler=None)
