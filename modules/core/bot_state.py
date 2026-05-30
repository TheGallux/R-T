"""
Bot State class.
"""

from dataclasses import dataclass, field

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

    screenshot_channel: int = 0
