"""
The `profile` command.
Shows a mem
"""

from discord.ext import commands


from modules.utils.get_fetched_member import get_fetched_member
from modules.utils.is_admin import discord_user_is_admin
from modules.utils.pretty_print import pretty_print
from modules.utils.logger import get_logger


logger = get_logger(__name__)


class Profile(commands.Cog):
    """
    The `profile` command class.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def profile(self, ctx, player: str = None):
        """
        The `profile` command.
        """
        logger.info("`profile` command used by `%s` (%s)", ctx.author,
                    ctx.author.id)

        if player is None:
            author_tag = self.bot.state.linker.get(str(ctx.author.id), '')

            if author_tag == '':
                await ctx.send("Author is not linked yet!")
                return

            if author_tag is None:
                await ctx.send("User not in club!")
                return

        else:
            if not discord_user_is_admin(self.bot, ctx.author.id):
                await ctx.send(
                    "You must be an admin to use `profile` "
                    "for another player!"
                )
                return

            member = get_fetched_member(self.bot, "name", player)

            if member is None:
                await ctx.send(f"Could not find player `{player}`!")
                return

            author_tag = member["tag"]

        print(author_tag)
        member = get_fetched_member(self.bot, "tag", author_tag).copy()
        del member["brawlers"]

        author_tag = self.bot.state.linker.get(str(ctx.author.id), '')
        if author_tag == '':
            await ctx.send("Author is not linked yet!")
            return

        if author_tag is None:
            await ctx.send("User not in club!")
            return

        await ctx.send("```yaml\n" + pretty_print(member) + "```")


async def setup(bot):
    """
    The function used to load the `member` command.
    """
    logger.info("Loading `profile` cog.")

    await bot.add_cog(Profile(bot))
