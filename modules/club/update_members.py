"""
The `update_members` loop.
Every five minutes, it calls the Brawl Stars API to fetch club members
"""

from os import environ
from discord.ext import commands, tasks

import requests


class UpdateMembersLoop(commands.Cog):
    """
    The `update_members` loop class.
    """

    def __init__(self, bot):
        self.bot = bot
        self.update_members.start()

    @tasks.loop(minutes=5)
    async def update_members(self):
        """
        The `update_members` loop.
        """

        url = (
            "https://api.brawlstars.com/v1/clubs/"
            f"%23{environ['CLUB_TAG'][1:]}/members"
        )
        headers = {"Authorization": f"Bearer {environ['API_KEY_BS']}"}

        try:
            response = requests.get(url, headers=headers, timeout=(3, 10))

        except requests.exceptions.Timeout:
            print("[club][update_members.py][update_members] - "
                  "Request timed out")

        if not response.ok:
            print("[club][update_members.py][update_members] - Error fetching "
                  "club members !", response)
            return

        self.bot.state["members"] = []
        data = response.json().get("items", [])

        for member in data:
            parsed_member = {
                "name": member["name"],
                "tag": member["tag"],
                "role": member["role"],
                "trophies": member["trophies"]
            }

            self.bot.state["members"].append(parsed_member)

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
