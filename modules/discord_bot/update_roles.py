"""
The `update_roles` loop.
Every hour for every member linked in the Discord, it will :
    - update the trophies count role
    - update the current ranked rank role
    - update the current rank in the club role
"""

import asyncio

from os import environ
import discord
from discord.ext import commands, tasks

from modules.utils.debug_messages import print_load_message
from modules.utils.get_fetched_member import get_fetched_member


def get_trophies_role(tr: int, roles: list[int], tr_threshold: int) -> int:
    """
    Returns the correct role based on trophies.
    The last role is a lower bound.
    """

    index = tr // tr_threshold

    if index >= len(roles):
        index = len(roles) - 1

    return roles[index]


async def sync_role_category(member, category_roles, target_role):
    """
    Removes all category roles from the member and adds the target role if
    necessary.
    """

    if target_role in member.roles:
        return

    to_remove = [role for role in category_roles if role in member.roles]

    for role in to_remove:
        await member.remove_roles(role)

    await member.add_roles(target_role)


class UpdateRolesLoop(commands.Cog):
    """
    The `update_roles` loop class.
    """

    def __init__(self, bot):
        self.bot = bot

        trophies_roles_id = environ["TROPHIES_ROLES_ID"]
        self.bot.state["trophies_roles_id"] = \
            [int(role) for role in trophies_roles_id.split(',')]
        self.bot.state["tr_threshold"] = int(environ["TROPHIES_THRESHOLD"])

        self.update_roles.start()

    @tasks.loop(hours=1)
    async def update_roles(self):
        """
        The `update_roles` loop.
        """

        await asyncio.gather(
            self.update_trophies(),
            self.update_club_roles(),
            self.update_ranked_roles(),
        )

    async def update_trophies(self):
        """
        Synchronizes trophies roles for all linked Discord members.
        """

        guild = self.bot.get_guild(self.bot.state["club_id"])
        linker = self.bot.state["linker"]

        for member_id in linker:
            member = await guild.fetch_member(int(member_id))
            if member is None:
                continue

            role_id = get_trophies_role(
                get_fetched_member(self.bot,
                                   "tag",
                                   linker[member_id])["trophies"],
                self.bot.state["trophies_roles_id"],
                self.bot.state["tr_threshold"])

            try:
                await sync_role_category(member,
                                         [guild.get_role(role) for role in
                                          self.bot.state["trophies_roles_id"]],
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
