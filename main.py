from dotenv import load_dotenv
import os

import discord
from discord.ext import commands

import aiohttp
import asyncio

import requests
from datetime import datetime, timedelta
import json

from random import randint

# Intents (obligatoires pour lire les messages)
intents = discord.Intents.default()
intents.message_content = True

# Préfixe des commandes
bot = commands.Bot(command_prefix=".", intents=intents)

load_dotenv()
API_KEY = os.environ["API_KEY_BS"]
RT_TOKEN = os.environ["RT_TOKEN"]


@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")


# Commande simple
@bot.command()
async def ping(ctx):
    await ctx.send("Pong 🏓")


@bot.command()
async def flip(ctx):
    if randint(0, 1) == 0:
        await ctx.send("Pile!")
    else:
        await ctx.send("Face!")


members_list = []
last_members = None


async def _members(ctx, display: bool):
    global last_members, members_list

    chunk_size = 10
    diff = None if last_members is None else datetime.now() - last_members

    if diff is not None and diff < timedelta(minutes=5):
        if display:
            remaining = (timedelta(minutes=5) - diff).total_seconds()
            await ctx.send(f"Next fetch in {int(remaining // 60)} minutes.")

    else:
        last_members = datetime.now()
        members_list = []
        if display:
            await ctx.send("New members command")
        url = "https://api.brawlstars.com/v1/clubs/%232LJ8YLCVQ/members"

        headers = {"Authorization": f"Bearer {API_KEY}"}

        response = requests.get(url, headers=headers)

        if display:
            await ctx.send(response.status_code)
        data = response.json()
        members = data.get("items", [])

        for i in range(0, len(members), chunk_size):
            chunk = members[i: i + chunk_size]

            for m in chunk:
                name = m["name"]
                tag = m["tag"]
                role = m["role"]
                trophies = m["trophies"]

                members_list.append(
                    {"name": name,
                     "tag": tag,
                     "role": role,
                     "trophies": trophies}
                )

    if display:
        for i in range(0, len(members_list), chunk_size):
            text = "\n".join([str(v) for v in members_list[i: i + chunk_size]])
            await ctx.send(text)


# Commande simple
@bot.command()
async def members(ctx):
    await _members(ctx, True)


@bot.command()
async def member(ctx, member_name: str):
    await _members(ctx, False)

    found = False
    for member in members_list:
        if member["name"] == member_name:
            await ctx.send(member)
            found = True

    if not found:
        await ctx.send(f"{member_name} not found!")


@bot.command()
async def profile(ctx, member_name: str):
    await _members(ctx, False)

    await ctx.send(f"Recherche de : {member_name}")
    found = False
    for member in members_list:
        if member["name"] == member_name:
            tag = member["tag"]
            found = True

    if not found:
        await ctx.send(f"{member_name} not found!")
        return

    url = f"https://api.brawlstars.com/v1/players/%23{tag[1:]}"

    headers = {"Authorization": f"Bearer {API_KEY}"}

    response = requests.get(url, headers=headers)
    data = response.json()

    text = json.dumps(data, indent=2)

    chunks = [text[i: i + 1900] for i in range(0, len(text), 1900)]

    for chunk in chunks:
        await ctx.send(f"```json\n{chunk}\n```")


async def fetch_player(session, member):
    url = f"https://api.brawlstars.com/v1/players/%23{member['tag'][1:]}"

    headers = {"Authorization": f"Bearer {API_KEY}"}

    async with session.get(url, headers=headers) as response:
        data = await response.json()

        member["current_elo"] = data.get("rankedElo", 0)
        member["highest_elo"] = data.get("highestSeasonRankedElo", 0)
        member["best_elo"] = data.get("highestAllTimeRankedElo", 0)


async def _update_ranked():
    await _members(None, False)

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_player(session, member) for member in members_list]

        await asyncio.gather(*tasks)


@bot.command()
async def ranked(ctx, level="current"):
    level = level.lower()
    if level not in ("current", "highest", "best"):
        await ctx.send(f"{level} should be 'current', 'highest' or 'best'")
        return

    await _update_ranked()
    await ctx.send("Finished fetching players")
    members_list.sort(key=lambda player: player[f"{level}_elo"])

    chunk_size = 10
    for i in range(0, len(members_list), chunk_size):
        text = "\n".join([str(v) for v in members_list[i: i + chunk_size]])
        await ctx.send(text)


@bot.command()
async def trophies(ctx):
    await _members(None, False)
    members_list.sort(key=lambda player: player["trophies"])

    chunk_size = 10
    for i in range(0, len(members_list), chunk_size):
        text = "\n".join([str(v) for v in members_list[i: i + chunk_size]])
        await ctx.send(text)


@bot.command()
async def battlelog(ctx, member_name=""):
    await _members(None, False)

    found = False
    for member in members_list:
        if member["name"] == member_name:
            tag = member["tag"]
            found = True

    if not found:
        await ctx.send(f"{member_name} not found!")
        return

    url = f"https://api.brawlstars.com/v1/players/%23{tag[1:]}/battlelog"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    response = requests.get(url, headers=headers)
    data = response.json()["items"]

    battlelog = []
    for battle in data:
        try:
            this_battle = {}
            this_battle["battleTime"] = battle["battleTime"]
            this_battle["result"] = battle["battle"]["result"]
            this_battle["teammates"] = []
            player_team = battle["battle"]["teams"][0]  # FIXME
            this_battle["teammates"].append(
                (player_team[0]["tag"], player_team[0]["name"])
            )
            this_battle["teammates"].append(
                (player_team[1]["tag"], player_team[1]["name"])
            )
            this_battle["teammates"].append(
                (player_team[2]["tag"], player_team[2]["name"])
            )
            this_battle["brawler"] = player_team[0]["brawler"]["name"]  # FIXME

            battlelog.append(this_battle)
        except Exception:
            print("Crash on this battle")
            print(json.dumps(battle, indent=2))

    text = json.dumps(battlelog, indent=2)

    chunks = [text[i: i + 1900] for i in range(0, len(text), 1900)]

    for chunk in chunks:
        await ctx.send(f"```json\n{chunk}\n```")


# Réaction automatique à un message
""""@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "salut" in message.content.lower():
        await message.channel.send("Salut 👋")

    await bot.process_commands(message)"""

# Lancement du bot
bot.run(RT_TOKEN)
