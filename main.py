import os
import sys
import logging

import discord
from discord.ext import commands
from config import load_env

discord.utils.setup_logging(root=True)
logger = logging.getLogger(__name__)

load_env(".env")
token = os.environ.get("APP_TOKEN")
guild_id = discord.Object(os.environ.get("GUILD_ID"))
if not token:
    sys.exit("Error: APP_TOKEN is not set. Add it to your .env file or environment.")

intents = discord.Intents.default()
intents.message_content = True

class MovieNightBot(commands.Bot):
    async def setup_hook(self):
        self.tree.copy_global_to(guild=guild_id)
        await self.tree.sync(guild=guild_id)

    async def on_ready(self):
        assert self.user is not None
        logger.info('Logged in as %s (ID: %s)', self.user, self.user.id)


bot = MovieNightBot(command_prefix='/', intents=intents)


@bot.tree.command(name='test', description='test slash command')
async def test(interaction: discord.Interaction):
    await interaction.response.send_message('hello world!')

bot.run(token, log_handler=None)
