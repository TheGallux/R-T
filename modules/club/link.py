"""
The `link` command.
Links a Discord member to a Brawl Stars account.
"""

import json
import discord

from discord.ext import commands

from modules.utils.logger import get_logger
from modules.utils.get_fetched_member import get_fetched_member

logger = get_logger(__name__)


class Link(commands.Cog):
    """
    The `link` command class.
    """

    def __init__(self, bot):
        self.bot = bot
        logger.info("Initialized `link` cog")

    def update_json(self, path: str):
        """
        Updates the json file contaning the dictionnary Discord UUID - Brawl
        Stars tag.
        """

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.bot.state.linker, f, indent=4)

        logger.info("Updated linker file (%s)", path)

    @commands.command()
    async def link(self, ctx, discord_member: discord.Member):
        """
        The `link` command.
        """
        logger.info("`link` command used by `%s` (%s)", ctx.author,
                    ctx.author.id)

        tag = get_fetched_member(self.bot, "name",
                                 discord_member.display_name).get("tag", None)

        if tag is None:
            await ctx.send("User not found!")
            logger.warning("No Brawl Stars account found for `%s`",
                           discord_member.display_name)
            return

        self.bot.state.linker[str(discord_member.id)] = tag

        self.update_json("link.json")

        logger.info("Linked Discord member `%s` to Brawl Stars tag `%s`",
                    discord_member.id,
                    tag)
        await ctx.send(f"Successfully linked `{discord_member.display_name}`"
                       f"to `{tag}`.")

    @commands.command()
    async def unlink(self, ctx, discord_member: discord.Member):
        """
        The `unlink` command.
        """
        logger.info("`unlink` command used by `%s` (`%s`)",
                    ctx.author.display_name, ctx.author.id)
        discord_id = str(discord_member.id)

        if discord_id not in self.bot.state.linker:
            logger.warning("`%s` is not linked", discord_member.id)
            await ctx.send(f"{discord_member.name} is not linked!")
            return

        del self.bot.state.linker[discord_id]

        self.update_json("link.json")

        logger.info("Unlinked Discord member `%s`", discord_member.id)
        await ctx.send(f"Successfully unlinked {discord_member.mention}.")


async def setup(bot):
    """
    The function used to load the `member` command.
    """
    logger.info("Loading `link` cog.")

    await bot.add_cog(Link(bot))
