import logging

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


class MovieNightBot(commands.Bot):
    def __init__(self, guild_id: discord.Object, **kwargs):
        super().__init__(**kwargs)
        self.guild_id = guild_id

    async def setup_hook(self):
        await self.load_extension('commands')
        self.tree.copy_global_to(guild=self.guild_id)
        await self.tree.sync(guild=self.guild_id)

    async def on_ready(self):
        assert self.user is not None
        logger.info('Logged in as %s (ID: %s)', self.user, self.user.id)
