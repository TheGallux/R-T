"""
Update the JSON file containing containing for each Discord ID:
    - their tag in Brawl Stars
    - the nomber of chaos drops they have
    - the number of currency they have
"""

import json

from modules.utils.logger import get_logger

logger = get_logger(__name__)


def update_json(bot):
    """
    Updates the json file contaning the dictionnary Discord UUID - Brawl
    Stars tag.
    """

    to_dump = {discord_id: {
        "tag": bot.state.linker.get(discord_id, None),
        "chaos_drop": bot.state.chaos_drop.get(discord_id, 0),
        "currency": bot.state.currency.get(discord_id, 0)
    } for discord_id in bot.state.linker}

    with open(bot.state.linker_name, "w", encoding="utf-8") as f:
        json.dump(to_dump, f, indent=4)

    logger.info("Updated linker file (%s)", bot.state.linker_name)
