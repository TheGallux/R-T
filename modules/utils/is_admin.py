"""
Functions which retrieves if a user (Discord/Brawl Stars) is an administrator
(An administrator is either the President or a Vice-President)
"""


def discord_user_is_admin(bot, author_id):
    """
    Returns true if the Discord user sending the message is associated to an
    administrator account.
    """

    return bot.state["linker"].get(str(author_id), '') in bot.state["admins"]
