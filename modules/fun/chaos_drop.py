"""
On it, it chaos_drops a coins and either prints "Heads!" or "Tails"
"""

from math import log2
from random import choices, randint, sample

import asyncio
import discord
from discord.ext import commands

from modules.utils.is_admin import discord_user_is_admin
from modules.utils.logger import get_logger
from modules.utils.update_json import update_json

logger = get_logger(__name__)

RARITIES = ["SUPER_RARE", "EPIC", "MYTHIC", "LEGENDARY", "ULTRA"]

RARITY_WEIGHTS = [52, 28, 12, 6, 2]

DIVISIONS = [1, 2, 4, 8]

DIVISION_WEIGHTS = [70, 20, 8, 2]

emojis = {
    "RARE": "<:Rare_Chaos_Drop:1510363248023572691>",
    "SUPER_RARE": "<:Super_Rare_Chaos_Drop:1510363280022044753>",
    "EPIC": "<:Epic_Chaos_Drop:1510363136773853395>",
    "MYTHIC": "<:Mythic_Chaos_Drop:1510363187323732108>",
    "LEGENDARY": "<:Legendary_Chaos_Drop:1510363160484384980>",
    "ULTRA": "<:Ultra_Chaos_Drop:1510363304374046821>",

    "CHROMA": "<:chroma_credits:1545132333542416395>",
    "CHROMAS": "<:chroma_credits_stack:1545132295818580079>",
}


class ChaosDrop(commands.Cog):
    """
    The `chaos_drop` command class.
    """

    def __init__(self, bot):
        self.bot = bot
        logger.info("Initialized `chaos_drop` cog")

    @commands.group()
    async def chaos_drop(self, ctx):
        """
        The `chaos_drop` command group.
        """
        logger.info("`member` command used by `%s` (%s)", ctx.author,
                    ctx.author.id)

        if ctx.invoked_subcommand is None:
            await ctx.send(
                "Available commands: `open`, `list`, `give`, `remove`"
            )

    @chaos_drop.command()
    async def open(self, ctx):
        """
        Open a chaos drop.
        """

        if self.bot.state.chaos_drop[str(ctx.author.id)] <= 0:
            await ctx.send("User don't have enough chaos drops!")
            return
        self.bot.state.chaos_drop[str(ctx.author.id)] -= 1

        rarity = choices(RARITIES, weights=RARITY_WEIGHTS, k=1)[0]
        division = choices(DIVISIONS, weights=DIVISION_WEIGHTS, k=1)[0]

        animation = [
            [None] * randint(1, 3)
            for _ in range(RARITIES.index(rarity) + 1)
        ]

        total_taps = sum(len(level) for level in animation)

        upgrade_taps = set(sample(range(total_taps), k=int(log2(division))))

        current_rarity = "RARE"
        current_division = 1

        def get_display():
            """
            Return the current chaos drop display.
            """
            if current_division == 8:
                return "\n".join(
                    4 * emojis[current_rarity]
                    for _ in range(2)
                )

            return current_division * emojis[current_rarity]

        msg = await ctx.send(get_display())

        tap_index = 0

        for i, level in enumerate(animation):
            for _ in level:

                if tap_index in upgrade_taps:
                    current_division *= 2

                await msg.edit(content=get_display())
                await asyncio.sleep(.5)

                tap_index += 1

            current_rarity = RARITIES[i]

        await msg.edit(content=get_display())

        amount_earned = division * (2 ** (1 + RARITIES.index(rarity)))
        self.bot.state.currency[str(ctx.author.id)] += amount_earned

        await ctx.send(f"{ctx.author.display_name}, you earned {amount_earned}"
                       f" {emojis["CHROMA" + "S"
                                  if amount_earned != 1 else '']}")
        update_json(self.bot)

    @chaos_drop.command()
    async def list(self, ctx):
        """
        List chaos drops.
        """
        if self.bot.state.linker.get(str(ctx.author.id), None) is None:
            await ctx.send("User isn't linked!")
            return

        chaos_drops = self.bot.state.chaos_drop[str(ctx.author.id)]
        currency = self.bot.state.currency[str(ctx.author.id)]
        await ctx.send(f"User \"{ctx.author.display_name}\" have "
                       f"{chaos_drops} {emojis["RARE"]} and "
                       f"{currency} {emojis["CHROMAS"
                                            if currency > 1 else "CHROMA"]}")

    @chaos_drop.command()
    async def give(self, ctx, member: discord.Member, amount: int):
        """
        Give a chaos drop to a player.
        """
        if not discord_user_is_admin(self.bot, ctx.author.id):
            await ctx.send("User isn't an admin!")
            return

        if self.bot.state.linker.get(str(member.id), None) is None:
            await ctx.send(f"{member.display_name} isn't linked!")
            return

        self.bot.state.chaos_drop[str(member.id)] = \
            max(0, self.bot.state.chaos_drop[str(member.id)] + amount)
        update_json(self.bot)

    @chaos_drop.command()
    async def remove(self, ctx, member, amount: int):
        """
        Remove a chaos drop from a player.
        """
        await self.give(ctx, member, -amount)


async def setup(bot):
    """
    The function used to load the `chaos_drop` command.
    """
    logger.info("Loading `chaos_drop` cog.")

    await bot.add_cog(ChaosDrop(bot))
