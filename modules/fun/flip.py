"""
The `flip` command.
On it, it flips a coins and either prints "Heads!" or "Tails"
"""

from random import choice, randint

import asyncio
from discord.ext import commands

from modules.utils.logger import get_logger


logger = get_logger(__name__)


class Flip(commands.Cog):
    """
    The `flip` command class.
    """

    def __init__(self, bot):
        self.bot = bot
        logger.info("Initialized `flip` cog")

    @commands.command()
    async def flip(self, ctx):
        """
        The `flip` command.
        """
        logger.info("`member` command used by `%s` (%s)", ctx.author,
                    ctx.author.id)

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
    logger.info("Loading `flip` cog.")

    await bot.add_cog(Flip(bot))
