"""
Retrieves a fetched member from the bot state using a key/value pair.
"""


def get_fetched_member(bot, key: str, value: str):
    """
    Retrieves a fetched member from the bot state using a key/value pair.
    """

    for member in bot.state.members:
        if member.get(key) == value:
            return member

    return None
