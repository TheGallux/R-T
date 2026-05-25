"""
The `flip` command.
On it, it flips a coins and either prints "Heads!" or "Tails"
"""

from random import choice, randint

import asyncio
from discord.ext import commands

from modules.utils.debug_messages import print_load_message


class Flip(commands.Cog):
    """
    The `flip` command class.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def flip(self, ctx):
        """
        The `flip` command.
        """

        msg = await ctx.send("Flipping the coin...")

        results = ["Heads", "Tails"]
        for i in range(randint(4, 8)):
            await asyncio.sleep(.5)
            await msg.edit(content=f"{results[i % 2]}")

        await msg.edit(content=f"It landed on **{choice(results)}**!")


async def setup(bot):
    """
    The function used to load the `flip` command.
    """

    print_load_message(__file__, "command")
    await bot.add_cog(Flip(bot))
