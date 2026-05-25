"""
The `members` command.
Lists all memebrs in the club.
"""

from discord.ext import commands

from modules.utils.debug_messages import print_load_message
from modules.utils.is_admin import discord_user_is_admin
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

        if not discord_user_is_admin(self.bot, ctx.message.author.id):
            await ctx.send("Command user is not an administrator !")
            return

        members_list = self.bot.state["members"]
        chunk_size = 6

        for i in range(0, len(members_list), chunk_size):
            text = pretty_print(members_list[i: i + chunk_size])
            await ctx.send(f"```yaml\n{text}```")


async def setup(bot):
    """
    The function used to load the `members` command.
    """

    print_load_message(__file__, "command")
    await bot.add_cog(Members(bot))
