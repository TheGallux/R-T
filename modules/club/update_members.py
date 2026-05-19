"""
The `update_members` loop.
Every five minutes, it calls the Brawl Stars API to fetch club members
"""

import asyncio

from os import environ
from discord.ext import commands, tasks

import aiohttp


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
                print(
                    "[club][update_members][fetch_members] - "
                    "Error fetching members:", response.status
                )
                return

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
            print("[club][update_members][fetch_player]:",
                  "Error fetching player:", tag, response.status)
            return None

        return await response.json()


class UpdateMembersLoop(commands.Cog):
    """
    The `update_members` loop class.
    """

    def __init__(self, bot):
        self.bot = bot
        self.update_members.start()

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

        # Fetching data
        try:
            data = await fetch_members()

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print("[club][fetch_members][fetch_members] - Unexpected error:",
                  e)

        try:
            data2 = await self.upgrade_fetched_members(
                [member["tag"] for member in data]
            )

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print("[club][fetch_members][upgrade_fetched_members] - "
                  "Unexpected error:", e)

        # Using fetched data
        club_map = {m["tag"]: m for m in data}
        player_map = {m["tag"]: m for m in data2}
        updated_members = []

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

            updated_members.append(parsed_member)

        self.bot.state["members"] = updated_members

    # ---

    @commands.command()
    async def display_members(self, ctx):
        """
        FIXME: To remove. Temporary to test the passive members fetching.
        """
        members_list = self.bot.state["members"]
        chunk_size = 10

        for i in range(0, len(members_list), chunk_size):
            text = "\n".join([str(v) for v in members_list[i: i + chunk_size]])
            await ctx.send(text)


async def setup(bot):
    """
    The function used to load the `update_members` loop.
    """

    print("Loading `update_members` loop from `club` module.")
    await bot.add_cog(UpdateMembersLoop(bot))
