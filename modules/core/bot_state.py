"""
Bot State class.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import discord

# pylint: disable=too-many-instance-attributes


@dataclass
class BotState:
    """
    Bot State class.
    """

    retrieved_members: bool = False

    guild = None

    members: list = field(default_factory=list)

    linker: dict = field(default_factory=dict)

    trophies_roles_id: list[int] = field(default_factory=list)
    trophies_threshold: list[int] = field(default_factory=list)

    ranked_roles_id: list[int] = field(default_factory=list)
    ranked_threshold: list[int] = field(default_factory=list)

    club_roles_id: list[int] = field(default_factory=list)

    is_playing: bool = field(default=False)
    queue: bool = field(default_factory=list)
    voice_client: discord.voice_client.VoiceClient | None = field(default=None)

    screenshot_channel: int = 0

    start_time: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
