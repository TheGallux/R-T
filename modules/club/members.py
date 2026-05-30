"""
The `members` command.
Lists all memebrs in the club.
"""

from discord.ext import commands

from modules.utils.is_admin import discord_user_is_admin
from modules.utils.pretty_print import pretty_print
from modules.utils.logger import get_logger


logger = get_logger(__name__)


class Members(commands.Cog):
    """
    The `members` command class.
    """

    def __init__(self, bot):
        self.bot = bot
        logger.info("Initialized `members` cog")

    @commands.command()
    async def members(self, ctx):
        """
        The `members` command.
        """
        logger.info("`members` command used by `%s` (%s)", ctx.author,
                    ctx.author.id)

        if not discord_user_is_admin(self.bot, ctx.message.author.id):
            await ctx.send("Command user is not an administrator !")
            return

        members_list = self.bot.state.members
        chunk_size = 6

        for i in range(0, len(members_list), chunk_size):
            text = pretty_print(members_list[i: i + chunk_size])
            await ctx.send(f"```yaml\n{text}```")


async def setup(bot):
    """
    The function used to load the `members` command.
    """
    logger.info("Loading `members` cog.")

    await bot.add_cog(Members(bot))
