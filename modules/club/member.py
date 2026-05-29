"""
The `member` command.
Retrieve a member based on its name.
"""

from discord.ext import commands

from modules.utils.is_admin import discord_user_is_admin
from modules.utils.pretty_print import pretty_print
from modules.utils.get_fetched_member import get_fetched_member
from modules.utils.logger import get_logger


logger = get_logger(__name__)


class Member(commands.Cog):
    """
    The `member` command class.
    """

    def __init__(self, bot):
        self.bot = bot
        logger.info("Initialized `member` cog")

    @commands.command()
    async def member(self, ctx, member_name: str):
        """
        The `member` command.
        """
        logger.info("`member` command used by `%s` (%s)", ctx.author,
                    ctx.author.id)

        if not discord_user_is_admin(self.bot, ctx.message.author.id):
            await ctx.send("Command user is not an administrator !")
            return

        member = get_fetched_member(self.bot, "name", member_name)
        if member is not None:
            await ctx.send(f"```yaml\n{pretty_print(member)}```")
            return

        await ctx.send(f"{member_name} not found!")


async def setup(bot):
    """
    The function used to load the `member` command.
    """
    logger.info("Loading `member` cog.")

    await bot.add_cog(Member(bot))
