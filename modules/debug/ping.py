"""
The `ping` command.
On it, the bot display back "Pong!".
"""

from discord.ext import commands

from modules.utils.logger import get_logger


logger = get_logger(__name__)


class Ping(commands.Cog):
    """
    The `ping` command class.
    """

    def __init__(self, bot):
        self.bot = bot
        logger.info("Initialized `ping` cog")

    @commands.command()
    async def ping(self, ctx):
        """
        The `ping` command.
        """
        logger.info("`ping` command used by `%s` (%s)", ctx.author,
                    ctx.author.id)

        await ctx.send("Pong!")


async def setup(bot):
    """
    The function used to load the `ping` command.
    """
    logger.info("Loading `ping` cog.")

    await bot.add_cog(Ping(bot))
