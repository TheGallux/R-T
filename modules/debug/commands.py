"""
The `commands` command.
Displays all the commands available in the bot.
"""

from discord.ext import commands

from modules.utils.logger import get_logger


logger = get_logger(__name__)


class Commands(commands.Cog):
    """
    The `commands` command class.
    """

    def __init__(self, bot):
        self.bot = bot
        logger.info("Initialized `commands` cog")

    @commands.command()
    async def commands(self, ctx):
        """
        The `commands` command.
        """
        logger.info("`commands` command used by `%s` (%s)", ctx.author,
                    ctx.author.id)

        text = ""
        for cog_name, cog in self.bot.cogs.items():
            text += f"\n[{cog_name}]\n" if len(cog.get_commands()) != 0 else ''

            for command in cog.get_commands():
                text += f"    !{command.name}\n"

        await ctx.send(text[1:])


async def setup(bot):
    """
    The function used to load the `commands` command.
    """
    logger.info("Loading `commands` cog.")

    await bot.add_cog(Commands(bot))
