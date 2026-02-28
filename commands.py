import logging
from datetime import timedelta

import discord
from discord import HTTPException, InteractionResponded, app_commands, Forbidden
from discord.ext import commands
from httpx import HTTPStatusError

from cycle import CycleState, MovieNightCycle
from movies import Movie, MovieList
from utils import fetch_metadata, parse_time_from_str, validate_url

logger = logging.getLogger(__name__)


class Movies(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._cycle: MovieNightCycle | None = None
        self._poll_message: discord.Message | None = None
        self._ml = MovieList()

    @app_commands.command(name="help", description="Learn how to use Movie Night Bot")
    async def help(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "**Movie Night Bot**\n\n"
            "**How it works:**\n"
            "1. Run `/movienight` to kick off a movie night cycle\n"
            "2. During the nomination window, anyone can use `/addmovie` to submit a movie\n"
            "3. When nominations close, a poll is created automatically\n"
            "4. When voting closes, the winner is announced and pinned\n\n"
            "**Commands:**\n"
            "`/movienight nomination_window:<duration> voting_window:<duration> schedule_every:<duration>` — Start a movie night\n"
            "`/addmovie <title>` — Add a movie to the nomination list\n"
            "`/help` — Show this message\n\n"
            "**Duration format:** `30m`, `1h`, `2d`",
            ephemeral=True,
        )

    @app_commands.command(
        name="movienight",
        description="Start a movie night — set nomination and voting windows",
    )
    async def plan_movie_nights(
        self,
        interaction: discord.Interaction,
        nomination_window: str,
        voting_window: str,
        # PLANNED: schedule_every: str,
    ):
        async def on_nominations_open(deadline):
            await channel.send(
                "**Movie Night nominations are open!**\n"
                f"Submit your picks with `/addmovie` — nominations close <t:{int(deadline.timestamp())}:R>"
            )

        async def on_voting_open(deadline):
            movies = await self._ml.all()
            if not movies:
                await channel.send("No movies were nominated. Cancelling the cycle.")
                self._cycle.cancel()
                self._cycle = None
                return
            # discord polls must last a minimum of an hour
            poll_duration = (
                voting_window
                if voting_window >= timedelta(hours=1)
                else timedelta(hours=1)
            )
            poll = discord.Poll(
                question="Which movie should we watch?",
                duration=poll_duration,
            )
            for movie in movies:
                poll.add_answer(text=movie.name)
            try:
                self._poll_message = await channel.send(
                    f"**Nominations are closed — time to vote!**\n"
                    f"Voting closes <t:{int(deadline.timestamp())}:R>",
                    poll=poll,
                )
            except Forbidden:
                logger.error(
                    "Missing permissions to send poll in channel %s", channel.id
                )
                await channel.send(
                    "I don't have permission to create a poll here. Cancelling the cycle."
                )
                self._cycle.cancel()
                self._cycle = None
            except HTTPException as exc:
                logger.error("Failed to create poll: %s", exc)
                await channel.send("Failed to create the poll. Cancelling the cycle.")
                self._cycle.cancel()
                self._cycle = None

        async def on_cycle_complete():
            message = await self._poll_message.fetch()
            answers = message.poll.answers
            if all(a.vote_count == 0 for a in answers):
                await channel.send("No votes were cast. No winner this time!")
            else:
                top = max(a.vote_count for a in answers)
                winners = [a for a in answers if a.vote_count == top]
                if len(winners) > 1:
                    tied = ", ".join(f"**{a.text}**" for a in winners)
                    announcement = await channel.send(
                        f"It's a tie between {tied}! No winner declared."
                    )
                else:
                    announcement = await channel.send(
                        f"**The winner is: {winners[0].text}!**"
                    )
                    await announcement.pin()
            await self._ml.clear()
            self._poll_message = None
            self._cycle = None

        try:
            if self._cycle is not None:
                await interaction.response.send_message(
                    "A movie night cycle is already running.", ephemeral=True
                )
                return

            nomination_window = parse_time_from_str(nomination_window)
            voting_window = parse_time_from_str(voting_window)
            channel = interaction.channel

            self._cycle = MovieNightCycle(
                nomination_window,
                voting_window,
                on_nominations_open=on_nominations_open,
                on_voting_open=on_voting_open,
                on_cycle_complete=on_cycle_complete,
            )
            self._cycle.start()
            await interaction.response.send_message(
                "Movie night cycle started!", ephemeral=True
            )
        except HTTPException as exc:
            logger.error(exc)
        except InteractionResponded as exc:
            logger.error(exc)
        except ValueError as exc:
            logger.error(exc)
            await interaction.response.send_message(
                "Invalid duration format — use a number followed by `m`, `h`, or `d`. Example: `30m`, `1h`, `2d`",
                ephemeral=True,
            )

    @app_commands.command(
        name="addmovie", description="Add a movie to the nomination list"
    )
    async def addmovie(self, interaction: discord.Interaction, url: str):
        if self._cycle is None or self._cycle.current_state != CycleState.NOMINATING:
            await interaction.response.send_message(
                "Nominations aren't open right now.", ephemeral=True
            )
            return

        if not validate_url(url):
            await interaction.response.send_message(
                "Only IMDB and Letterboxd URLs are supported.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)
        try:
            title = await fetch_metadata(url)
            await self._ml.add(Movie(name=title, url=url))
            await interaction.followup.send(
                f"**{title}** added to the nominations.\n{url}", ephemeral=True
            )
        except HTTPStatusError as exc:
            logger.error(exc)
            await interaction.followup.send(
                "Couldn't fetch movie info — double check the URL and try again.",
                ephemeral=True,
            )
        except ValueError as exc:
            logger.error(exc)
            await interaction.followup.send(
                "Couldn't fetch movie info — double check the URL and try again.",
                ephemeral=True,
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Movies(bot))
