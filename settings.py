from pathlib import Path
import parser

CONFIG_PATH = Path("~/.config/smp/smp.conf").expanduser()
MACROS_PATH = Path("~/.config/smp/macros.json").expanduser()


def config(*args, generate=False):
    if generate or not CONFIG_PATH.exists():
        print("Generating default configuration file...")
        if not CONFIG_PATH.parent.exists():
            CONFIG_PATH.mkdir(parents=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(
                """[General]
# Path to all your songs and playlists
music_dir = ~/music
playlist_dir = ~/music/playlists
# Also equivalent to %(music_dir)s/playlists

# Changed the default prompt. You can still enable the old one
# by uncommenting it
prompt = '$ '
#prompt = ' '

autocomplete = 1
# 0 - No autocomplete (not recommended)
# 1 - Unambiguous autocomplete (default)
# 2 - Full autocomplete: If your input is ambiguous, smp will list
# all possible commands and let you choose

default_volume = 100
# Sets the starting volume. Must be between 0 and 100

ls_sep = ", "
# Controls how `ls` separates each element of output. Setting this to
# " " allows you to use its output directly without having to remove commas
"""
            )
        print(f"Config file created in {CONFIG_PATH}")
        return
    if not args:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            # Need to specify encoding otherwise it could crash on Windows
            # if your config has unicode characters for the prompt
            print(f"Config file located in {CONFIG_PATH}")
            print(f.read())
            return
    cmd, *_ = args
    if cmd == "generate":
        config(generate=True)


def reload_cfg(startup=True):
    Settings.read_config(
        parser.get_config(CONFIG_PATH), startup
    )


class Settings:
    music_dir: lambda f: Path(f).expanduser() = "~"
    playlist_dir: lambda f: Path(f).expanduser() = "~"
    # Changed to ~ to ensure directory exists as invalid directory would
    # make the program crash on startup. if this still crashes,
    # you have bigger problems
    prompt: str = " "
    autocomplete: int = 1
    default_volume: float = 80
    ls_sep: str = ", "
    _cfg_dict = {}

    @classmethod
    def read_config(cls, cfg_dict, startup=True):
        for key in cfg_dict:
            cls._cfg_dict[key] = cfg_dict[key]
        attrs = {"music_dir", "playlist_dir", "prompt",
                 "autocomplete", "default_volume", "ls_sep"}
        for attr in attrs:
            type_ = cls.__annotations__[attr]
            try:
                new_val = cls._cfg_dict[attr]
            except KeyError:
                config(generate=True)
                reload_cfg()
                return
            try:
                setattr(cls, attr, type_(new_val))
            except ValueError:
                if startup:
                    print(
                        f"Invalid value specified for setting {attr}:"
                        f" {new_val}"
                    )
                else:
                    print(
                        f"\nInvalid value specified for setting {attr}: "
                        f"{new_val}"
                    )
                    print(end=cls.prompt, flush=True)
        if not Settings.music_dir.exists():
            print("CRITICAL: specified music directory does not exist")
            Settings.music_dir = Path("~").expanduser()
        if not Settings.playlist_dir.exists():
            print("CRITICAL: specified playlist directory does not exist")
            Settings.playlist_dir = Path("~").expanduser()
        if not CONFIG_PATH.exists():
            config()
        if not MACROS_PATH.exists():
            MACROS_PATH.write_text("{}")
