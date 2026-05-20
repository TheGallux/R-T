"""
The `members` command.
Lists all memebrs in the club.
"""

from discord.ext import commands

from modules.utils.pretty_print import pretty_print


class Members(commands.Cog):
    """
    The `members` command class.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def members(self, ctx):
        """
        The `members` command.
        """
        members_list = self.bot.state["members"]
        chunk_size = 6

        for i in range(0, len(members_list), chunk_size):
            text = pretty_print(members_list[i: i + chunk_size])
            await ctx.send(f"```yaml\n{text}```")


async def setup(bot):
    """
    The function used to load the `members` command.
    """

    print("Loading `members` command from `code` module.")
    await bot.add_cog(Members(bot))
