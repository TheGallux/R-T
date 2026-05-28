"""
Entry point for R-T.
"""

import asyncio
import json
import os
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

        if "utils" in root:
            continue

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
    Launches commands once the bot is uable on Discord.
    """

    bot.state["guild"] = bot.get_guild(int(os.getenv("GUILD_ID")))
    print(f"Logged in as {bot.user}")


@bot.command()
async def reload(ctx, extension):
    """
    Allows reloading modules when running using `!reload <module>`
    """

    await bot.reload_extension(f"modules.{extension}")
    await ctx.send(f"Reloaded {extension}")


async def main():
    """
    Launches the bot, and inits its memory.
    """

    async with bot:
        bot.state = {}
        bot.state["retrieved_members"] = False

        bot.state["trophies_roles_id"] = \
            [int(role) for role in os.getenv("TROPHIES_ROLES_ID").split(',')]
        bot.state["trophies_threshold"] = \
            [int(n) for n in os.getenv("TROPHIES_THRESHOLDS").split(',')]

        bot.state["ranked_roles_id"] = \
            [int(role) for role in os.getenv("RANKED_ROLES_ID").split(',')]
        bot.state["ranked_threshold"] = \
            [int(n) for n in os.getenv("RANKED_THRESHOLDS").split(',')]

        with open("link.json", 'r', encoding="utf-8") as f:
            bot.state["linker"] = json.loads(''.join(f.readlines()))

        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
