import discord
from discord import app_commands
from discord.ext import commands


class Movies(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="addmovie", description="Add a movie to the voting list")
    async def addmovie(self, interaction: discord.Interaction, movie: str):
        # will probably want to validate and make sure the movie is a valid string
        # react with an emoji to confirm movie has been added and/or send a confirmation message to 
        # allow users to edit or cancel
        pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Movies(bot))
