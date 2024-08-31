from pathlib import Path
from smp_help import command
from player import Player
import parser

CONFIG_PATH = Path("~/.config/smp/smp.conf").expanduser()
MACROS_PATH = Path("~/.config/smp/macros.json").expanduser()
CFG_TEMPLATE = """[General]
# Path to all your songs and playlists
{} = {}
{} = {}

# Changed the default prompt. You can still enable the old one
# by uncommenting it
{} = '{}'
#prompt = ' '

{} = {}
# 0 - No autocomplete (not recommended)
# 1 - Unambiguous autocomplete (default)
# 2 - Full autocomplete: If your input is ambiguous, smp will list
# all possible commands and let you choose

{} = {}
# Sets the starting volume. Must be between 0 and 100

ls_sep = ", "
# Controls how `ls` separates each element of output. Setting this to
# " " allows you to use its output directly without having to remove commas
"""


def config(*args, generate=False):
    if generate:
        print("Generating default configuration file...")
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(
                """[General]
# Path to all your songs and playlists
music_dir = ~/music
playlist_dir = ~/music/playlists

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
    else:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            # Need to specify encoding otherwise it could crash on Windows
            # if your config has unicode characters for the prompt
            print(f"Config file located in {CONFIG_PATH}")
            print(f.read())


def reload_cfg(startup=True):
    Settings.read_config(parser.get_config(CONFIG_PATH), startup)


@command(Player)
def config_wizard(*args):
    Player.awaiting_commands = False
    empty_config = False
    if not CONFIG_PATH.exists():
        CONFIG_PATH.touch()
        print("No configuration file detected, starting wizard...")
        empty_config = True
    if empty_config:
        default = input(
            "Do you want to use the default config or create custom config?(d/c) "
        ).lower()
        if default == "d":
            print("default")
            config(generate=True)
            return
    elif "generate" not in args:
        print("generate")
        config(generate=False)
        return
    else:
        confirm = input(
            "Generating a new config will override your existing one. Continue?(y/n) "
        ).lower()
        if confirm != "y":
            print("Cancelled.")
            return
    cfg_options = {
        "music_dir": (
            "Enter the directory containing your music or leave blank for default (~/music): ",
            "~/music",
            str,
        ),
        "playlist_dir": (
            "Enter the directory containing your playlists or leave blank for default (~/music/playlists): ",
            "~/music/playlists",
            str,
        ),
        "prompt": (
            "Enter your desired prompt string or leave blank for default ('$ ') ",
            "$ ",
            str,
        ),
        "autocomplete": (
            "Enter your desired autocomplete level (0 - off, 1 - default, 2 - full) or leave blank: ",
            1,
            int,
        ),
        "default_volume": (
            "Enter your desired default volume from 0-100 (default 100) ",
            100,
            int,
        ),
    }
    user_choices = {}
    for key, (prompt, default, type_) in cfg_options.items():
        choice = None
        if type_ is not str:
            # No need to convert if we want a string, and we know the only other option is an int
            while choice is None:
                choice = input(prompt) or default
                try:
                    choice = type_(choice)
                except ValueError:
                    print("Input must be an integer")
                    continue
                if choice is None:
                    continue
                if key == "autocomplete" and choice not in range(0, 3):
                    print("Autocomplete must be between 0 and 2")
                    choice = None
                elif key == "default_volume" and choice not in range(0, 101):
                    print("Default volume must be between 0 and 100")
                    choice = None
        else:
            choice = input(prompt) or default
        user_choices[key] = choice

    formatted_choices = []
    for choice in user_choices.items():
        formatted_choices.extend(choice)
    CONFIG_PATH.write_text(CFG_TEMPLATE.format(*formatted_choices))
    print(f"New config saved at {CONFIG_PATH}")
    Player.awaiting_commands = True


class Settings:
    music_dir: lambda f: Path(f).expanduser() = "~"
    playlist_dir: lambda f: Path(f).expanduser() = "~"
    # Changed to ~ to ensure directory exists as invalid directory would
    # make the program crash on startup. if this still crashes,
    # you have bigger problems
    prompt: str = "$ "
    autocomplete: int = 1
    default_volume: float = 80
    ls_sep: str = ", "
    _cfg_dict = {}

    @classmethod
    def read_config(cls, cfg_dict, startup=True):
        if not CONFIG_PATH.exists():
            config_wizard()
            reload_cfg()
        if not MACROS_PATH.exists():
            MACROS_PATH.write_text("{}")
        for key in cfg_dict:
            cls._cfg_dict[key] = cfg_dict[key]
        attrs = {
            "music_dir",
            "playlist_dir",
            "prompt",
            "autocomplete",
            "default_volume",
            "ls_sep",
        }
        for attr in attrs:
            type_ = cls.__annotations__[attr]
            try:
                new_val = cls._cfg_dict[attr]
            except KeyError:
                config_wizard()
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
