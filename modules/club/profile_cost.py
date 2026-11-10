"""
The 'profile_cost' command for calculating the resources invested in
Brawl Stars

The command calculates the total amount of Coins, Power Points, and Credits
spent on the brawlers of a linked club member, including power levels, Gears,
Gadgets, Star Powers, Hypercharges, and Buffies.
"""

from discord.ext import commands

from modules.utils.get_fetched_member import get_fetched_member
from modules.utils.is_admin import discord_user_is_admin
from modules.utils.logger import get_logger
from modules.utils.pretty_print import pretty_print

logger = get_logger(__name__)


UPGRADE_COSTS = {
    1: {"power_points": 0, "coins": 0},
    2: {"power_points": 20, "coins": 20},
    3: {"power_points": 50, "coins": 55},
    4: {"power_points": 100, "coins": 130},
    5: {"power_points": 180, "coins": 270},
    6: {"power_points": 310, "coins": 560},
    7: {"power_points": 520, "coins": 1040},
    8: {"power_points": 860, "coins": 1840},
    9: {"power_points": 1410, "coins": 3090},
    10: {"power_points": 2300, "coins": 4965},
    11: {"power_points": 3740, "coins": 7765},
}

CREDITS_BY_RARITY = {
    "STARTING": 0,
    "RARE": 160,
    "SUPER_RARE": 430,
    "EPIC": 925,
    "MYTHIC": 1900,
    "LEGENDARY": 3800,
    "ULTRA_LEGENDARY": 5500,
}

BRAWLERS_BY_RARITY = {
    "STARTING": ["SHELLY"],

    "RARE": [
        "COLT", "BULL", "BROCK", "BARLEY", "NITA", "EL PRIMO", "POCO", "ROSA"
    ],

    "SUPER_RARE": [
        "RICO", "JESSIE", "DYNAMIKE", "DARRYL", "PENNY", "TICK", "CARL",
        "8-BIT", "JACKY", "GUS"
    ],

    "EPIC": [
        "BO", "PIPER", "PAM", "FRANK", "BIBI", "BEA", "EMZ", "GALE", "NANI",
        "COLETTE", "EDGAR", "STU", "BELLE", "GROM", "GRIFF", "ASH", "LOLA",
        "BONNIE", "SAM", "MANDY", "MAISIE", "HANK", "PEARL", "LARRY & LAWRIE",
        "ANGELO", "BERRY", "SHADE", "MEEPLE", "TRUNK", "BOLT"
    ],

    "MYTHIC": [
        "MORTIS", "TARA", "GENE", "MR. P", "MAX", "SPROUT", "LOU", "BYRON",
        "RUFFS", "SQUEAK", "BUZZ", "FANG", "EVE", "JANET", "OTIS", "BUSTER",
        "GRAY", "R-T", "WILLOW", "DOUG", "CHUCK", "CHARLIE", "MICO", "MELODIE",
        "LILY", "CLANCY", "MOE", "JUJU", "OLLIE", "LUMI", "FINX", "JAE-YONG",
        "ALLI", "MINA", "ZIGGY", "GIGI", "GLOWY", "NAJIA", "DAMIAN",
        "STARR NOVA", "WENDY", "COSMO", "VINCE", "REY", "RUBY"
    ],

    "LEGENDARY": [
        "SPIKE", "CROW", "LEON", "SANDY", "SURGE", "AMBER", "MEG", "CHESTER",
        "CORDELIUS", "KIT", "DRACO", "KENJI", "PIERCE", "NORI",
        "THUNDER FROGS"
    ],

    "ULTRA_LEGENDARY": [
        "KAZE", "SIRIUS"
    ],
}

BRAWLER_CREDITS = {
    brawler: CREDITS_BY_RARITY[rarity]
    for rarity, brawlers in BRAWLERS_BY_RARITY.items()
    for brawler in brawlers
}

GEAR_COST = 1000
GADGET_COST = 1000
STAR_POWER_COST = 2000
HYPERCHARGE_COST = 5000
BUFFIE_COINS_COST = 1000
BUFFIE_PP_COST = 1000


class ProfileCost(commands.Cog):
    """
    The `profile_cost` command class.
    """

    def __init__(self, bot):
        self.bot = bot
        logger.info("Initialized `profile_cost` cog")

    @commands.command()
    async def profile_cost(self, ctx, player: str = None):
        """
        The `profile_cost` command.
        """
        logger.info("`profile_cost` command used by `%s` (%s)", ctx.author,
                    ctx.author.id)

        if player is None:
            # Normal user: use their linked account
            author_tag = self.bot.state.linker.get(str(ctx.author.id), '')

            if author_tag == '':
                await ctx.send("Author is not linked yet!")
                return

            if author_tag is None:
                await ctx.send("User not in club!")
                return

        else:
            if not discord_user_is_admin(self.bot, ctx.author.id):
                await ctx.send("You must be an admin to use `profile_cost` for"
                               " another player!")
                return

            author_tag = get_fetched_member(self.bot, "name", player)["tag"]

            if author_tag is None:
                await ctx.send(f"Could not find player `{player}`!")
                return

        member = get_fetched_member(self.bot, "tag", author_tag)

        resources = {
            "coins": 0,
            "power_points": 0,
            "credits": member["fame"]
        }

        for brawler in member["brawlers"]:
            # rarity of the brawler
            resources["credits"] += BRAWLER_CREDITS[brawler["name"]]

            # levels
            resources["coins"] += UPGRADE_COSTS[brawler["power"]]["coins"]
            resources["power_points"] += \
                UPGRADE_COSTS[brawler["power"]]["power_points"]

            # gears
            resources["coins"] += GEAR_COST * len(brawler["gears"])

            # gadgets
            resources["coins"] += GADGET_COST * len(brawler["gadgets"])

            # star powers
            resources["coins"] += STAR_POWER_COST * len(brawler["starPowers"])

            # hypercharge
            resources["coins"] += \
                HYPERCHARGE_COST * len(brawler["hyperCharges"])

            # buffies
            number_of_buffies = sum(value is True for value in
                                    brawler["buffies"].values())
            resources["coins"] += BUFFIE_COINS_COST * number_of_buffies
            resources["power_points"] += BUFFIE_PP_COST * number_of_buffies

        await ctx.send("```yaml\n" + pretty_print(resources) + "```")


async def setup(bot):
    """
    The function used to load the `profile_cost` command.
    """
    logger.info("Loading `profile_cost` cog.")

    await bot.add_cog(ProfileCost(bot))
