"""
The `ping` command.
On it, the bot display back "Pong!".
"""

from discord.ext import commands


class Ping(commands.Cog):
    """
    The `ping` command class.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """
        The `ping` command.
        """

        await ctx.send("Pong!")


async def setup(bot):
    """
    The function used to load the `ping` command.
    """

    print("Loading `ping` command from `debug` module.")
    await bot.add_cog(Ping(bot))
