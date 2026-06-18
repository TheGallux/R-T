"""
The `update_members` loop.
Every five minutes, it calls the Brawl Stars API to fetch club members
"""

import asyncio

from os import environ
from discord.ext import commands, tasks

import aiohttp

from modules.utils.logger import get_logger


logger = get_logger(__name__)


async def fetch_members():
    """
    A function to fetch the members of the club, done async.
    """

    url = (
        "https://api.brawlstars.com/v1/clubs/"
        f"%23{environ['CLUB_TAG'][1:]}/members"
    )
    headers = {
        "Authorization": f"Bearer {environ['API_KEY_BS']}"
    }

    timeout = aiohttp.ClientTimeout(total=10)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, headers=headers) as response:

            if response.status != 200:
                logger.error("Error fetching members: %s", response.status)
                return
            logger.info("Succesfully fetched members")

            data = await response.json()

    return data.get("items", [])


async def fetch_player(session, tag: str):
    """
    Fetch a player data using the players/{tag} endpoint
    """

    url = (
        "https://api.brawlstars.com/v1/players/"
        f"%23{tag[1:]}"
    )
    headers = {
        "Authorization": f"Bearer {environ['API_KEY_BS']}"
    }

    async with session.get(url, headers=headers) as response:

        if response.status != 200:
            logger.error("Error fetching player: %s", tag)
            return None
        logger.debug("Succesfully fetched player %s", tag)

        return await response.json()


class UpdateMembersLoop(commands.Cog):
    """
    The `update_members` loop class.
    """

    def __init__(self, bot):
        self.bot = bot
        self.update_members.start()
        logger.info("Initialized `update_members` cog")

    async def upgrade_fetched_members(self, tag_list: list[str]):
        """
        Adds extra data (player stats) to club members.
        """

        timeout = aiohttp.ClientTimeout(total=10)

        async with aiohttp.ClientSession(timeout=timeout) as session:

            tasks_to_run = [
                fetch_player(session, tag)
                for tag in tag_list
            ]

            results = await asyncio.gather(*tasks_to_run)

        return [r for r in results if r is not None]

    @tasks.loop(minutes=5)
    async def update_members(self):
        """
        The `update_members` loop.
        """
        logger.info("Running `update_members` loop")

        # Fetching data
        try:
            data = await fetch_members()
            logger.info("Sucessfully fetched %s club members.", len(data))

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.error("Unexpected error fetching members: %s", e)

        try:
            data2 = await self.upgrade_fetched_members(
                [member["tag"] for member in data]
            )
            logger.info("Sucessfully fetched %s enriched players.", len(data2))

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.error("Unexpected error fetching enriched players: %s", e)

        # Using fetched data
        club_map = {m["tag"]: m for m in data}
        player_map = {m["tag"]: m for m in data2}
        updated_members = []
        admins = []

        for tag, club_member in club_map.items():
            player_data = player_map.get(tag, {})

            parsed_member = {
                # base club data
                "name": club_member.get("name"),
                "tag": tag,
                "role": club_member.get("role"),
                "trophies": club_member.get("trophies"),

                # enriched player data
                "ranked_elo": player_data.get("rankedElo"),
                "highest_season_ranked_elo":
                    player_data.get("highestSeasonRankedElo"),
                "highest_all_time_ranked_elo":
                    player_data.get("highestAllTimeRankedElo"),
            }

            if parsed_member["role"] in ("president", "vicePresident"):
                admins.append(parsed_member["tag"])

            updated_members.append(parsed_member)

        logger.info(
            "update_members completed: %s members, %s admins",
            len(updated_members), len(admins)
        )
        self.bot.state.members = updated_members
        self.bot.state.admins = admins
        self.bot.state.retrieved_members = True

    @update_members.error
    async def update_members_error(self, error):
        """
        Function if the loop ever fails.
        Prints the Exception to help debug.
        """

        logger.error("'update_members' loop crashed", exc_info=error)


async def setup(bot):
    """
    The function used to load the `update_members` loop.
    """
    logger.info("Loading `update_members` cog.")

    await bot.add_cog(UpdateMembersLoop(bot))
