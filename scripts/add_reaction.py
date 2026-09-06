"""
Add an emoji to a message.
"""

import os
import sys

import discord

from dotenv import load_dotenv

load_dotenv()

if len(sys.argv) < 4:
    print("USAGE: python scripts/add_reaction.py <CHANNEL_ID> <MESSAGE_ID> "
          "<EMOJI>")
    print("Exemple:")
    print("python scripts/add_reaction.py "
          "1410420737386221588 "
          "1545909710467768380 "
          "'👍'")
    sys.exit(1)

CHANNEL_ID = int(sys.argv[1])
MESSAGE_ID = int(sys.argv[2])
EMOJI = sys.argv[3]

intents = discord.Intents.default()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    """
    Launches the bot.
    """

    print(f"Logged in as {client.user}")

    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        print("Channel not found.")
        return

    try:
        message = await channel.fetch_message(MESSAGE_ID)
        await message.add_reaction(EMOJI)
        print("Reaction added!")
    except discord.NotFound:
        print("Message not found.")
    except discord.Forbidden:
        print("I don't have permission to react to this message.")
    except discord.HTTPException as e:
        print(f"Discord API error: {e}")

    await client.close()


client.run(os.getenv("RT_TOKEN"))
