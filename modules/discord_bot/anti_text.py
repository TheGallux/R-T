"""
The `anti-text` event.
Takes SCREENSHOT_CHANNEL in the environment, and deletes every message which
does not contains a message. If it does contain a message, it create a thread
so users can speak on it.
"""

from os import environ
from discord.ext import commands

from modules.utils.debug_messages import print_load_message


class AntiTextEvent(commands.Cog):
    """
    The `anti_text` event class.
    """

    def __init__(self, bot):
        self.bot = bot
        self.screenshot_channel_id = int(environ["SCREENSHOT_CHANNEL"])

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        The `anti_text` event.
        """

        if message.author.bot:
            return

        if message.channel.id != self.screenshot_channel_id:
            return

        if not message.attachments:
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, tu ne peux pas envoyer uniquement "
                "du texte dans ce salon!",
                delete_after=5
            )

        else:
            await message.add_reaction("<:thumbs_up:1509338751770296441>")
            await message.add_reaction("<:thumbs_down:1509338725019287703>")

            thread_name = message.content
            if not thread_name:
                thread_name = f"Thread de '{message.author.display_name}'"
            thread_name = thread_name[:100]

            await message.create_thread(
                name=thread_name,
                auto_archive_duration=1440
            )


async def setup(bot):
    """
    The function used to load the `anti_text` event.
    """

    print_load_message(__file__, "event")
    await bot.add_cog(AntiTextEvent(bot))
