"""
Entry point for R-T.
"""

import asyncio
import json
import os
from dotenv import load_dotenv

import discord
from discord.ext import commands

from modules.core.bot_state import BotState
from modules.utils.logger import get_logger
from modules.utils.is_admin import discord_user_is_admin


logger = get_logger(__name__)

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

        if "utils" in root or "core" in root:
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

                logger.info("Finish loading `%s`", module)


@bot.event
async def on_ready():
    """
    Launches commands once the bot is uable on Discord.
    """

    bot.state.guild = bot.get_guild(int(os.getenv("GUILD_ID")))
    logger.info("Logged in as `%s`", bot.user)


@bot.command()
async def reload(ctx, extension):
    """
    Allows reloading modules when running using `!reload <module>`
    """
    logger.info("`reload` command used by `%s` (%s)", ctx.author,
                ctx.author.id)

    if not discord_user_is_admin(bot, ctx.author.id):
        await ctx.send("You aren't an admin!")
        logger.info("User tried 'reload' but isn't an admin! (%s)",
                    ctx.author.id)
        return

    await bot.reload_extension(f"modules.{extension}")
    await ctx.send(f"Reloaded {extension}")


async def main():
    """
    Launches the bot, and inits its memory.
    """

    async with bot:
        bot.state = BotState()
        bot.state.retrieved_members = False
        bot.state.screenshot_channel = int(os.getenv("SCREENSHOT_CHANNEL"))
        bot.state.linker_name = os.getenv("LINKER_NAME")
        bot.state.db_name = os.getenv("DB_NAME")

        bot.state.trophies_roles_id = \
            [int(role) for role in os.getenv("TROPHIES_ROLES_ID").split(',')]
        bot.state.trophies_threshold = \
            [int(n) for n in os.getenv("TROPHIES_THRESHOLDS").split(',')]

        bot.state.ranked_roles_id = \
            [int(role) for role in os.getenv("RANKED_ROLES_ID").split(',')]
        bot.state.ranked_threshold = \
            [int(n) for n in os.getenv("RANKED_THRESHOLDS").split(',')]

        bot.state.club_roles_id = \
            [int(role) for role in os.getenv("CLUB_ROLES_ID").split(',')]

        with open(bot.state.linker_name, 'r', encoding="utf-8") as f:
            json_read = json.loads(''.join(f.readlines()))
        bot.state.linker = {k: json_read[k].get("tag") for k in json_read}
        bot.state.chaos_drop = {k: json_read[k].get("chaos_drop")
                                for k in json_read}
        bot.state.currency = {k: json_read[k].get("currency")
                              for k in json_read}

        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
