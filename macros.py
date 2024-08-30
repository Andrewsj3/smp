from pathlib import Path
from smp_common import autocomplete
import json
from player import Player
from smp_help import command

CONFIG_DIR = Path("~/.config/smp").expanduser()
MACROS_PATH = CONFIG_DIR / "macros.json"
M_CMDS = {
    "add": lambda *args: add_macro(*args),
    "save": lambda *args: save_macro(*args),
    "delete": lambda *args: del_macro(*args),
}

CMDS = {
    "config",
    "eval",
    "exit",
    "delete",
    "forward",
    "help",
    "list",
    "loop",
    "ls",
    "macro",
    "pause",
    "play",
    "queue",
    "quit",
    "rename",
    "repeat",
    "rewind",
    "seek",
    "stop",
    "time",
    "unpause",
    "volume",
}


@command(Player)
def macro(*args):
    if not args:
        for key, value in Player.macros.items():
            print(f"{key} -> {value}")
        return
    cmd, *args = args
    if cmd in M_CMDS:
        M_CMDS[cmd](*args)
    else:
        autocomplete(cmd, M_CMDS, *args)


def load_macros():
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir()
        with open(MACROS_PATH, "w") as f:
            f.write("{}")
        return {}
    else:
        with open(MACROS_PATH) as f:
            return json.load(f)


@command(Player, "macro add", requires_args=True)
def add_macro(*args):
    mcr, *args = args
    for arg in args:
        if arg == mcr:
            print("Recursive macros are not allowed")
            return
        if mcr in Player.macros.get(arg, []):
            print("Cyclical macros are not allowed")
            del Player.macros[arg]
            return
    if mcr in CMDS:
        print("Macros can't be named existing commands")
        return
    if not args:
        print("Macro needs at least one argument")
        return
    Player.macros[mcr] = " ".join(args)


@command(Player, "macro delete", requires_args=True)
def del_macro(*args):
    saved_macros = load_macros()
    for arg in args:
        if arg in Player.macros:
            del Player.macros[arg]
            if arg in saved_macros:
                del saved_macros[arg]
        else:
            print("Macro not found")
    with open(MACROS_PATH, "w") as f:
        json.dump(saved_macros, f)


@command(Player, "macro save", requires_args=True)
def save_macro(*args):
    saved_macros = load_macros()
    for mcr in args:
        if mcr in saved_macros:
            replace = input(
                "This macro already exists. "
                "Do you want to replace it? (y/n) "
            ).lower()
            if replace == "y":
                saved_macros[mcr] = Player.macros[mcr]
        else:
            saved_macros[mcr] = Player.macros[mcr]
    with open(MACROS_PATH, "w") as f:
        json.dump(saved_macros, f)
