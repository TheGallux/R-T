"""
The `member` command.
Retrieve a membar based on its name.
"""

from discord.ext import commands


class Member(commands.Cog):
    """
    The `member` command class.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def member(self, ctx, member_name: str):
        """
        The `member` command.
        """

        for member in self.bot.state.get("members", []):
            if member["name"] == member_name:
                await ctx.send(member)
                return

        await ctx.send(f"{member_name} not found!")


async def setup(bot):
    """
    The function used to load the `member` command.
    """

    print("Loading `member` command from `code` module.")
    await bot.add_cog(Member(bot))
