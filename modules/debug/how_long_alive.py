"""
The `how_long_alive` command.
On it, the bot display back for how long it's been running.
"""

from datetime import datetime, timezone

from discord.ext import commands

from modules.utils.logger import get_logger


logger = get_logger(__name__)


class HowLongAlive(commands.Cog):
    """
    The `how_long_alive` command class.
    """

    def __init__(self, bot):
        self.bot = bot
        logger.info("Initialized `how_long_alive` cog")

    @commands.command()
    async def how_long_alive(self, ctx):
        """
        The `how_long_alive` command.
        """
        logger.info("`how_long_alive` command used by `%s` (%s)", ctx.author,
                    ctx.author.id)

        uptime = datetime.now(timezone.utc) - self.bot.state.start_time

        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if days:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

        await ctx.send(f"I've been alive for {', '.join(parts)}.")


async def setup(bot):
    """
    The function used to load the `how_long_alive` command.
    """
    logger.info("Loading `how_long_alive` cog.")

    await bot.add_cog(HowLongAlive(bot))
