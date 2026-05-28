"""
The `update_roles` loop.
Every hour for every member linked in the Discord, it will :
    - update the trophies count role
    - update the current ranked rank role
    - update the current rank in the club role
"""

import asyncio

import discord
from discord.ext import commands, tasks

from modules.utils.debug_messages import print_load_message
from modules.utils.get_fetched_member import get_fetched_member


def get_role(n: int, roles: list[int], thresholds: list[int]) -> int:
    """
    Returns the correct role based on a list of thresholds (sorted).
    The last role is a lower bound.
    """

    for i, threshold in enumerate(thresholds):
        if n < threshold:
            return roles[i]

    return roles[-1]


async def sync_role_category(member, category_roles, target_role):
    """
    Removes all category roles from the member and adds the target role if
    necessary.
    """

    if target_role in member.roles:
        return

    to_remove = [role for role in category_roles if role in member.roles]

    await member.remove_roles(*to_remove)

    await member.add_roles(target_role)


class UpdateRolesLoop(commands.Cog):
    """
    The `update_roles` loop class.
    """

    def __init__(self, bot):
        self.bot = bot
        self.update_roles.start()

    @tasks.loop(hours=1)
    async def update_roles(self):
        """
        The `update_roles` loop.
        """

        state = self.bot.state
        await asyncio.gather(
            self.update_roles_with_thresholds("trophies",
                                              state["trophies_roles_id"],
                                              state["trophies_threshold"]),
            self.update_roles_with_thresholds("ranked_elo",
                                              state["ranked_roles_id"],
                                              state["ranked_threshold"]),
            self.update_ranked_roles(),
        )

    async def update_roles_with_thresholds(self,
                                           x: str,
                                           roles_id: list[str],
                                           thresholds: list[int]):
        """
        Synchronizes trophies roles for all linked Discord members.
        """

        guild = self.bot.state["guild"]
        linker = self.bot.state["linker"]

        for discord_id in linker:
            member = await guild.fetch_member(int(discord_id))
            if member is None:
                continue

            role_id = get_role(
                get_fetched_member(self.bot,
                                   "tag",
                                   linker[discord_id])[x],
                roles_id,
                thresholds)

            try:
                await sync_role_category(member,
                                         [guild.get_role(role) for role in
                                          roles_id],
                                         guild.get_role(role_id))
                print(f"Adding {guild.get_role(role_id)} to {member.name}")

            except discord.Forbidden:
                print("Missing permissions or role hierarchy issue")

    async def update_club_roles(self):
        """
        Synchronizes club roles for all linked Discord members.
        """

    async def update_ranked_roles(self):
        """
        Synchronizes ranked roles for all linked Discord members.
        """

    @update_roles.before_loop
    async def before_update_roles(self):
        """
        Function before launching cog.
        It waits for the members to be fetched.
        """
        await self.bot.wait_until_ready()

        while not self.bot.state["retrieved_members"]:
            print("Waiting for members to be retrieved...")
            await asyncio.sleep(1)


async def setup(bot):
    """
    The function used to load the `update_roles` loop.
    """

    print_load_message(__file__, "loop")
    await bot.add_cog(UpdateRolesLoop(bot))
