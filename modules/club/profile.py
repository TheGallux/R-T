"""
The `profile` command.
Shows a mem
"""

from discord.ext import commands

from modules.utils.pretty_print import pretty_print


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

        author_tag = self.bot.state["linker"].get(str(ctx.author.id), '')

        for member in self.bot.state["members"]:
            if member["tag"] == author_tag:
                await ctx.send("```yaml\n" + pretty_print(member) + "```")
                return

        await ctx.send("Author is not in the club or not linked yet!")


async def setup(bot):
    """
    The function used to load the `member` command.
    """

    print("Loading `profile` command from `club` module.")
    await bot.add_cog(Profile(bot))
