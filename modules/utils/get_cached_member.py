"""
Retrieve a Discord member using the guild cache first.
Falls back to an API fetch if necessary.
"""

import discord


async def get_cached_member(bot, discord_id: int):
    """
    Retrieve a Discord member using the guild cache first.
    Falls back to an API fetch if necessary.
    """

    guild = bot.state["guild"]

    member = guild.get_member(discord_id)

    if member is not None:
        return member

    try:
        member = await guild.fetch_member(discord_id)
        return member

    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
        return None
