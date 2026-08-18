"""
The `musics` command.

Provides YouTube music playback functionality for Discord voice channels.
"""

import asyncio

import discord
from discord.ext import commands
import yt_dlp

from modules.utils.logger import get_logger

logger = get_logger(__name__)


YDL_OPTIONS = {
    "format": "bestaudio/best",  # Ask YouTube for the best available audio.
    "noplaylist": True,          # Don't process playlists.
    "quiet": True,               # Keep yt-dlp quiet.
    "no_warnings": True,         # Avoid unnecessary warnings.
}

FFMPEG_OPTIONS = {
    "before_options": (
        "-reconnect 1 "                  # Allow FFmpeg to reconnect if the
                                         #     connection drops.
        "-reconnect_streamed 1 "         # Reconnect when the stream is
                                         #     considered a streamed resource.
        "-reconnect_delay_max 5 "        # Wait up to 5 seconds between
                                         #     reconnect attempts.
        "-reconnect_on_network_error 1"  # Reconnect when there is a network
                                         #     error.
    ),

    "options": "-vn",  # Discord only needs audio.

}


class YTMusic(commands.Cog):
    """
    YouTube music playback cog.
    """

    def __init__(self, bot):
        self.bot = bot
        logger.info("Initialized `musics` cog")

    # -------------------------
    # Utility
    # -------------------------
    def search_youtube(self, query: str):
        """
        Search YouTube for a song and return its URL and title.
        """

        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(
                f"ytsearch1:{query}",
                download=False
            )

            if not info.get("entries"):
                raise ValueError("No YouTube results found.")

            result = info["entries"][0]

            if not result.get("url"):
                result = ydl.extract_info(
                    result["webpage_url"],
                    download=False
                )

            return result["url"], result["title"]

    def get_source(self, url: str):
        """
        Extract the audio source URL and title from a YouTube URL.
        """

        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            return info["url"], info["title"]

    # Playback system
    async def play_next(self, ctx):
        """
        Play the next song in the music queue.
        """

        if len(self.bot.state.queue) == 0:
            self.bot.state.is_playing = False
            return

        self.bot.state.is_playing = True

        url, title = self.bot.state.queue.pop(0)

        def after_playing(error):
            if error:
                logger.error("Playback error: %s", error)

            fut = asyncio.run_coroutine_threadsafe(
                self.play_next(ctx), self.bot.loop
            )
            try:
                fut.result()
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error("Queue error: %s", e)

        self.bot.state.voice_client.play(
            discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS),
            after=after_playing
        )

        await ctx.send(f"🎶 Now playing: **{title}**")

    # -------------------------
    # Commands
    # -------------------------
    @commands.command()
    async def join(self, ctx):
        """Join user's voice channel."""
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("You're not in a voice channel.")
            return None

        channel = ctx.author.voice.channel
        voice_client = self.bot.state.voice_client

        try:
            if voice_client is None or not voice_client.is_connected():
                voice_client = await channel.connect()
                self.bot.state.voice_client = voice_client
            elif voice_client.channel != channel:
                await voice_client.move_to(channel)

            await ctx.send(f"Joined **{channel}**")
            return voice_client

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.exception("Failed to join voice channel %s (%s)", channel,
                             e)
            await ctx.send("❌ Failed to join the voice channel.")
            return None

    @commands.command()
    async def play(self, ctx, *, query: str):
        """
        Play a YouTube song (search or URL).
        """
        voice_client = self.bot.state.voice_client

        if voice_client is None or not voice_client.is_connected():
            voice_client = await self.join(ctx)

        if voice_client is None:
            return

        await ctx.send(f"🔎 Searching for: `{query}`")

        try:
            if "youtube.com" in query or "youtu.be" in query:
                url, title = self.get_source(query)
            else:
                url, title = self.search_youtube(query)

            self.bot.state.queue.append((url, title))

            await ctx.send(f"➕ Added to queue: **{title}**")

            if not self.bot.state.is_playing:
                await self.play_next(ctx)

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.exception("Play error for query: %s (%s)", query, e)
            await ctx.send("❌ Failed to play that track.")

    @commands.command()
    async def skip(self, ctx):
        """Skip current song."""
        if self.bot.state.voice_client and \
                self.bot.state.voice_client.is_playing():
            self.bot.state.voice_client.stop()
            await ctx.send("⏭ Skipped.")

    @commands.command()
    async def stop(self, ctx):
        """Stop playback and clear queue."""
        self.bot.state.queue.clear()

        if self.bot.state.voice_client:
            self.bot.state.voice_client.stop()
            await self.bot.state.voice_client.disconnect()
            self.bot.state.voice_client = None

        self.bot.state.is_playing = False
        await ctx.send("⏹ Stopped playback and cleared queue.")


async def setup(bot):
    """
    The function used to load the `musics` command.
    """

    logger.info("Loading `youtube music` cog.")
    await bot.add_cog(YTMusic(bot))
