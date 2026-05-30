"""
The `anti-text` event.
Takes SCREENSHOT_CHANNEL in the environment, and deletes every message which
does not contains a message. If it does contain a message, it create a thread
so users can speak on it.
"""

from discord.ext import commands

from modules.utils.logger import get_logger


logger = get_logger(__name__)


class AntiTextEvent(commands.Cog):
    """
    The `anti_text` event class.
    """

    def __init__(self, bot):
        self.bot = bot
        logger.info("Initialized `anti-text` cog")

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        The `anti_text` event.
        """
        logger.info("`anti-text` event launched by %s in %d (%d)",
                    message.author.display_name, message.channel.id,
                    message.id)

        if message.author.bot:
            logger.info("Message sent by R-T")
            return

        if message.channel.id != self.bot.state.screenshot_channel:
            logger.info("Message not sent in a tracked channel")
            return

        if not message.attachments:
            logger.info("Deleted message because not containing an image.")
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, tu ne peux pas envoyer uniquement "
                "du texte dans ce salon!",
                delete_after=5
            )

        else:
            logger.info("Message does contain an image, adding reactions "
                        "and creating thread.")
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
    logger.info("Loading `anti-text` cog.")

    await bot.add_cog(AntiTextEvent(bot))
