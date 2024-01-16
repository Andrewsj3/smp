import glob
from pathlib import Path
from settings import Settings


def flatten(lst):
    for elem in lst:
        if isinstance(elem, list):
            yield from flatten(elem)
        else:
            yield elem


def gen_files():
    return list(
        map(
            lambda f: Path(f).name,
            flatten(
                [
                    glob.glob(f"{Settings.music_dir}/*.{ext}")
                    for ext in SUPPORTED_TYPES
                ]
            ),
        )
    )


def autocomplete(ac_level, cmd, cmd_set, *args):
    if ac_level == 0:
        print("Autocomplete is disabled")
        return

    commands = [c for c in cmd_set if c.startswith(cmd)]
    if len(commands) == 1:
        cmd_set[commands[0]](*args)
    elif len(commands) == 0:
        print("Invalid command")
    else:
        if ac_level == 1:
            print(
                "Ambiguous command, could be one of " f"{', '.join(commands)}"
            )
        elif ac_level == 2:
            for idx, command in enumerate(commands, start=1):
                print(f"    {idx}: {command}")
            option = input(
                f"Select from the options above (1-{len(commands)}) or"
                " leave blank to cancel: "
            )
            if not option:
                return
            while option not in map(str, range(1, len(commands) + 1)):
                option = input(
                    f"Please enter a number from 1-{len(commands)}: "
                )
            cmd_set[commands[int(option) - 1]](*args)


def ac_songs(ac_level, song):
    if ac_level == 0:
        print(
            f"Couldn't find {song} in {Settings.music_dir}.\n"
            " If you meant to use autocomplete, you should enable it"
            " in your config file."
        )
        return False
    files = gen_files()
    songs = [s for s in files if s.startswith(song)]
    if len(songs) == 1:
        return songs[0]
    elif len(songs) == 0:
        print("Song not found")
        return False
    if ac_level == 1:
        print(f"Ambiguous song, could be one of {', '.join(songs)}")
    elif ac_level == 2:
        for idx, song in enumerate(songs, start=1):
            print(f"    {idx}: {song}")
        option = input(
            f"Select from the options above (1-{len(songs)}) or"
            " leave blank to cancel: "
        )
        if not option:
            return False
        while option not in map(str, range(1, len(songs) + 1)):
            option = input(f"Please enter a number from 1-{len(songs)}: ")
        return songs[int(option) - 1]


def timestamp(num):
    mins, secs = divmod(num, 60)
    if mins > 60:
        hours, mins = divmod(mins, 60)
        return f"{hours}:{mins:02}:{secs:02}"
    return f"{mins}:{secs:02}"




SUPPORTED_TYPES = ["mp3", "ogg", "wav", "flac", "opus"]
