import os
import pathlib
import sys


def get_datadir() -> pathlib.Path:

    """
    Returns a parent directory path
    where persistent application data can be stored.

    # linux: ~/.local/share
    # macOS: ~/Library/Application Support
    # windows: C:/Users/<USER>/AppData/Roaming
    """

    home = pathlib.Path.home()

    if sys.platform == "win32":
        return home / "AppData/Roaming"
    elif sys.platform == "linux":
        return home / ".local/share"
    elif sys.platform == "darwin":
        return home / "Library/Application Support"


def get_datapath(*, subdir: str = None, filename: str = None) -> pathlib.Path:
    path = get_datadir().joinpath("ModdbBot")
    if subdir is not None:
        path = path.joinpath(subdir)
    if not os.path.exists(path):
        os.makedirs(path)
    if filename is not None:
        path = path.joinpath(filename)
        if not os.path.exists(path):
            with open(path, 'w'):
                pass
    return path
