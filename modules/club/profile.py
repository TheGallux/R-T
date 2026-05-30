"""
The `profile` command.
Shows a mem
"""

from discord.ext import commands


from modules.utils.get_fetched_member import get_fetched_member
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
    async def profile(self, ctx):
        """
        The `profile` command.
        """
        logger.info("`profile` command used by `%s` (%s)", ctx.author,
                    ctx.author.id)

        author_tag = self.bot.state.linker.get(str(ctx.author.id), '')
        if author_tag == '':
            await ctx.send("Author is not linked yet!")
            return

        await ctx.send("```yaml\n" +
                       pretty_print(get_fetched_member(self.bot,
                                                       "tag",
                                                       author_tag))
                       + "```")


async def setup(bot):
    """
    The function used to load the `member` command.
    """
    logger.info("Loading `profile` cog.")

    await bot.add_cog(Profile(bot))
