"""
Leave all unallowed servers.
"""

import os

import discord

from dotenv import load_dotenv

load_dotenv()

ALLOWED_GUILD_IDS = {
    1410415778133577863,
    858740903676870676
}

intents = discord.Intents.default()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    """
    Launches the bot.
    """

    print(f"Logged in as {client.user}")

    for guild in client.guilds:
        if guild.id not in ALLOWED_GUILD_IDS:
            print(f"Leaving: {guild.name} ({guild.id})")
            await guild.leave()

    await client.close()


client.run(os.getenv("RT_TOKEN"))
