"""
The `member` command.
Retrieve a member based on its name.
"""

from discord.ext import commands

from modules.utils.debug_messages import print_load_message
from modules.utils.is_admin import discord_user_is_admin
from modules.utils.pretty_print import pretty_print


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

        if not discord_user_is_admin(self.bot, ctx.message.author.id):
            await ctx.send("Command user is not an administrator !")
            return

        for member in self.bot.state.get("members", []):
            if member["name"] == member_name:
                await ctx.send(f"```yaml\n{pretty_print(member)}```")
                return

        await ctx.send(f"{member_name} not found!")


async def setup(bot):
    """
    The function used to load the `member` command.
    """

    print_load_message(__file__, "command")
    await bot.add_cog(Member(bot))
