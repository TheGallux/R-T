"""
The `link` command.
Shows a mem
"""

import json
import discord

from discord.ext import commands


class Link(commands.Cog):
    """
    The `link` command class.
    """

    def __init__(self, bot):
        self.bot = bot

    def update_json(self, path: str):
        """
        Updates the json file contaning the dictionnary Discord UUID - Brawl
        Stars tag.
        """

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.bot.state["linker"], f, indent=4)

    @commands.command()
    async def link(self, ctx, discord_member: discord.Member):
        """
        The `link` command.
        """

        tag = None
        for member in self.bot.state["members"]:
            if member["name"] == discord_member.display_name:
                tag = member["tag"]
                break

        if tag is None:
            await ctx.send("User not found!")
            return

        self.bot.state["linker"][str(discord_member.id)] = tag

        self.update_json("link.json")

        await ctx.send("Successful or un truc comme ca")

    @commands.command()
    async def unlink(self, ctx, discord_member: discord.Member):
        """
        The `unlink` command.
        """
        discord_id = str(discord_member.id)

        if discord_id not in self.bot.state["linker"]:
            await ctx.send(f"{discord_member.name} is not linked!")
            return

        del self.bot.state["linker"][discord_id]

        self.update_json("link.json")

        await ctx.send("Successful or un truc comme ca")


async def setup(bot):
    """
    The function used to load the `member` command.
    """

    print("Loading `link` command from `club` module.")
    await bot.add_cog(Link(bot))
