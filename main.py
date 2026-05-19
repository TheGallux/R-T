"""
Entry point for R-T.
"""

import os
import asyncio
from dotenv import load_dotenv

import discord
from discord.ext import commands

load_dotenv()

TOKEN = os.getenv("RT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


async def load_extensions():
    """
    Load every modules of the bot.
    Commands are organized this way
    modules/
        <module_name>/
            __init__.py
            <command>.py
            <command>.py
        <module_name>/
            __init__.py
            <command>.py
            <command>.py
    """

    for root, _, files in os.walk("./modules"):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):

                path = os.path.join(root, file)

                module = (
                    path.removeprefix("./")
                    .replace("/", ".")
                    .replace("\\", ".")
                    .replace(".py", "")
                    )

                await bot.load_extension(module)

                print(f"Loaded {module}")


@bot.event
async def on_ready():
    """
    Launches commands once the bot is uable on Discord
    """

    print(f"Logged in as {bot.user}")


async def main():
    """
    Launches the bot
    """

    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
