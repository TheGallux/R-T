"""
Utility for printing standardized load messages for files and modules.
"""

from pathlib import Path


def print_load_message(filepath: str, type_: str) -> None:
    """
    Print a loading message for a file/module.
    """

    path = Path(filepath).resolve()

    filename_without_ext = path.stem
    directory_name = path.parent.name

    print(f"Loading `{filename_without_ext}` {type_} from `{directory_name}`"
          " module.")
