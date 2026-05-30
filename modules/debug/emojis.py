"""
The `emojis` command.
Displays all the emojis available to the bot.
"""

from discord.ext import commands

from modules.utils.logger import get_logger


logger = get_logger(__name__)


class Emojis(commands.Cog):
    """
    The `emojis` command class.
    """

    def __init__(self, bot):
        self.bot = bot
        logger.info("Initialized `emojis` cog")

    @commands.command()
    async def emojis(self, ctx):
        """
        The `emojis` command.
        """
        logger.info("`emojis` command used by `%s` (%s)", ctx.author,
                    ctx.author.id)

        text = ""
        for emoji in self.bot.emojis:
            prefix = "a" if emoji.animated else ""
            text += f"<{prefix}:{emoji.name}:{emoji.id}> "

            if len(text) > 900:
                await ctx.send(text)
                text = ""

        if len(text) != 0:
            await ctx.send(text)


async def setup(bot):
    """
    The function used to load the `emojis` command.
    """
    logger.info("Loading `emojis` cog.")

    await bot.add_cog(Emojis(bot))
