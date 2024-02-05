from pathlib import Path
from smp_common import autocomplete
import json
from settings import Settings
from player import Player
from smp_help import ihelp
MACROS_PATH = Path("~/.config/smp/macros.json").expanduser()
M_CMDS = {
    "add": lambda *args: add_macro(*args),
    "save": lambda *args: save_macro(*args),
    "delete": lambda *args: del_macro(*args)
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


def macro(*args):
    if not args:
        for key, value in Player.macros.items():
            print(f"{key} -> {value}")
        return
    cmd, *args = args
    if cmd in M_CMDS:
        M_CMDS[cmd](*args)
    else:
        autocomplete(Settings.autocomplete, cmd, M_CMDS, *args)


def load_macros():
    if not MACROS_PATH.exists():
        with open(MACROS_PATH, 'x') as f:
            f.write("{}")
        return {}
    else:
        with open(MACROS_PATH) as f:
            return json.load(f)


def add_macro(*args):
    if not args:
        ihelp("macro add")
        return
    mcr, *args = args
    if mcr in CMDS:
        print("Macros can't be named existing commands")
        return
    if not args:
        print("Macro needs at least one argument")
        return
    Player.macros[mcr] = " ".join(args)


def del_macro(*args):
    saved_macros = load_macros()
    if not args:
        ihelp("macro delete")
        return
    for arg in args:
        if arg in Player.macros:
            del Player.macros[arg]
            if arg in saved_macros:
                del saved_macros[arg]
        else:
            print("Macro not found")
    with open(MACROS_PATH, 'w') as f:
        json.dump(saved_macros, f)


def save_macro(*args):
    saved_macros = load_macros()
    if not args:
        return
    for mcr in args:
        if mcr in saved_macros:
            replace = input(
                "This macro already exists. "
                "Do you want to replace it? (y/n) ").lower()
            if replace == 'y':
                saved_macros[mcr] = Player.macros[mcr]
        else:
            saved_macros[mcr] = Player.macros[mcr]
    with open(MACROS_PATH, 'w') as f:
        json.dump(saved_macros, f)
