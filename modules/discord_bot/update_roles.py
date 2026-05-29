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

from modules.utils.get_cached_member import get_cached_member
from modules.utils.get_fetched_member import get_fetched_member
from modules.utils.logger import get_logger


logger = get_logger(__name__)


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
    logger.debug("Syncing `%s` from `%s`", target_role, member.display_name)

    if target_role in member.roles:
        logger.debug("`%s` already have `%s`", member.display_name,
                     target_role)
        return

    to_remove = [role for role in category_roles if role in member.roles]

    logger.debug("Removing `%s` from `%s`", to_remove, member.display_name)
    await member.remove_roles(*to_remove)

    logger.debug("Adding `%s` from `%s`", target_role, member.display_name)
    await member.add_roles(target_role)


class UpdateRolesLoop(commands.Cog):
    """
    The `update_roles` loop class.
    """

    def __init__(self, bot):
        self.bot = bot
        self.update_roles.start()
        logger.info("Initialized `update_roles` cog")

    @tasks.loop(hours=1)
    async def update_roles(self):
        """
        The `update_roles` loop.
        """
        logger.info("Running `update_roles` loop")

        state = self.bot.state
        await asyncio.gather(
            self.update_roles_with_thresholds("trophies",
                                              state["trophies_roles_id"],
                                              state["trophies_threshold"]),
            self.update_roles_with_thresholds("ranked_elo",
                                              state["ranked_roles_id"],
                                              state["ranked_threshold"]),
            self.update_club_roles(),
        )

        logger.info("`update_role` completed for %s linked members",
                    len(self.bot.state["linker"]))

    async def update_roles_with_thresholds(self,
                                           filt: str,
                                           roles_id: list[str],
                                           thresholds: list[int]):
        """
        Synchronizes trophies roles for all linked Discord members.
        """

        guild = self.bot.state["guild"]
        linker = self.bot.state["linker"]

        for discord_id in linker:
            member = await get_cached_member(self.bot, int(discord_id))
            if member is None:
                logger.warning("Discord member not found for discord_id=%s",
                               discord_id)
                continue

            role_id = get_role(
                get_fetched_member(self.bot,
                                   "tag",
                                   linker[discord_id])[filt],
                roles_id,
                thresholds)

            try:
                await sync_role_category(member,
                                         [guild.get_role(role) for role in
                                          roles_id],
                                         guild.get_role(role_id))

            except discord.Forbidden:
                logger.error(
                    "Failed syncing roles for %s (%s): missing permissions ",
                    member.display_name, member.id
                )

    async def update_club_roles(self):
        """
        Synchronizes club roles for all linked Discord members.
        """

    @update_roles.before_loop
    async def before_update_roles(self):
        """
        Function before launching cog.
        It waits for the members to be fetched.
        """
        await self.bot.wait_until_ready()

        while not self.bot.state["retrieved_members"]:
            logger.debug("Waiting member to be fetched...")
            await asyncio.sleep(1)


async def setup(bot):
    """
    The function used to load the `update_roles` loop.
    """
    logger.info("Loading `update_roles` cog.")

    await bot.add_cog(UpdateRolesLoop(bot))
