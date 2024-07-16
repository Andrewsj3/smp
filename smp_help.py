def parametrized(dec):
    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)

        return repl

    return layer


@parametrized
def command(func, player, topic=None, requires_args=False):
    def inner(*args, **kwargs):
        nonlocal topic
        topic = topic or func.__name__
        has_args = len(args) > 0
        if not has_args:
            if requires_args:
                ihelp(topic, player=player)
                return
        else:
            if args[0] in ("-h", "--help"):
                ihelp(topic, player=player)
                return
        func(*args, **kwargs)

    return inner


def ihelp(*topic, player):
    if topic:
        topic = " ".join(topic)
        if topic.startswith("queue") and len(topic.split()) == 2:
            _, subcmd = topic.split()
            print(Q_CMDS.get(subcmd, "No help for that"))
        elif topic.startswith("macro") and len(topic.split()) == 2:
            _, subcmd = topic.split()
            print(M_CMDS.get(subcmd, "No help for that"))
        else:
            print(CMDS.get(topic, "No help for that"))
        return

    print("Welcome to smp's interactive help utility!")
    print("Type `quit` or Ctrl-D to return to smp")
    print("Type `list` to see the list of available commands")
    print("Type `list queue` to see the list of queue subcommands")
    print("Type `list macro` to see the list of macro subcommands")
    print("Type `tips` for a list of tips")
    player.awaiting_commands = False
    while True:
        try:
            name = input(">>> ").lower().strip()
        except EOFError:
            print()
            player.awaiting_commands = True
            return
        if not name:
            continue
        if name == "quit":
            player.awaiting_commands = True
            return
        elif name == "list":
            print("\n".join(CMDS))
        elif name == "list queue":
            print("\n".join(Q_CMDS))
        elif name.startswith("queue") and len(name.split()) == 2:
            _, subcmd = name.split()
            print(Q_CMDS.get(subcmd, "No help for that"))
        elif name == "list macro":
            print("\n".join(M_CMDS))
        elif name.startswith("macro") and len(name.split()) == 2:
            _, subcmd = name.split()
            print(M_CMDS.get(subcmd, "No help for that"))
        elif name == "tips":
            print_tips()
        else:
            print(CMDS.get(name, "No help for that"))


def print_tips():
    print("""    1: smp allows unambiguous command abbreviation, which means
that you can shorten any command as long as it cannot be interpreted
as another command. e.g. `rep` is fine for repeat, but `re` could be
either rename, repeat, or rewind. This applies to songs and macros as well,
but not playlists.\n""")
    print("""    2: smp also features a macro system, allowing you to
combine multiple commands into one. You can even use them in other macros,
but be careful! Don't name them existing subcommands or you may accidentally
invoke a macro when you didn't mean to.
See `macro` in this help section for more.\n""")
    print("""    3: When starting smp, you can specify scripts to run
at startup. You can use this to do things like automatically load
and start a playlist. The `exec` command allows you to do this at any time
if you have scripts you prefer not to execute at launch.
Scripts live in ~/.config/smp/scripts/.
See `exec` for more.\n""")
    print("""    4: Some commands automatically show their help sections
when you don't provide arguments. Now, if you put '-h' or '--help' as the
first argument to any command, you can see its help section without having
to come here.\n""")


M_CMDS = {
    "add": """Usage: macro add <name> <*args>
Creates a macro called `name` which expands to `args`
when invoked. When creating a macro that expands to
multiple commands, remember that they must be separated
with a semicolon.""",
    "save": """Usage: macro save <*args>
For each macro in `args`, attempts to save the macro
in ~/.config/smp/macros.json. Will fail if the macro
does not exist.
This allows you to use this macro across sessions.""",
    "delete": """Usage: macro delete <*args>
For each macro in `args`, attempts to delete the macro.
If it is present in ~/.config/smp/macros.json, it is
also deleted there.""",
}
Q_CMDS = {
    "add": """Usage: queue add <*songs>
Adds songs to the end of the queue. Every argument after `add`
is treated as a song. Works with autocomplete.""",
    "clear": """Clears the current queue. This also stops the
queue from advancing if it is currently playing.""",
    "remove": """Usage: queue remove <*songs>
Works the same as `queue add`, but removes songs from wherever
they are in the queue.""",
    "play": """Starts playing the queue and advances the queue
index by 1. This means calling `queue play` again skips to the
next song, unless the current song is the last song, in which
case it will loop to the beginning.""",
    "next": """Skips to the next song, unless the current song
is the last song, in which case it will loop to the beginning.""",
    "prev": """Skips to the previous song, as long as the current
song is not the first song.""",
    "loop": """Toggles whether the queue should loop. After the
last song is finished, the queue will start from the start.""",
    "swap": """Swaps pairs of songs in the queue.""",
    "shuffle": """Toggles between the shuffled queue and the
normal queue. This command only shuffles the queue if it has
not already been shuffled.""",
    "randomize": """Randomizes the position of songs in the
shuffled queue. This command also implies `queue shuffle` if
the active queue is not the shuffled queue.""",
    "save": """Usage: queue save <filename>
Saves the unshuffled queue to <filename>.csv in the playlists
directory, overwriting it if it already exists.""",
    "load": """Usage: queue load <filename>
Loads the songs in <filename> into the current queue.""",
    "status": """Shows the previous song and the next song
(if applicable). Also shows the current song being played,
its index in the queue, the total length of the playlist,
and total time elapsed as a timestamp.
and a percentage. Only works if the queue is playing (paused is ok).""",
    "find": """Usage: queue find <*songs> | <*indexes>
For each song in songs, prints its position in the queue,
and the songs that come immediately before and after it (if applicable).
It also prints the previous 5 songs and the next 5 songs with
the desired song in blinking text. May not work on all systems.
Alternatively, you can enter a position to find out what song is
at that position.""",
}
CMDS = {
    "play": """Usage: play <song> [volume] [loops]
Looks for a song in the music directory (default ~/music).
If you have autocomplete enabled, you don't even have to type
out the whole song.

Specifying `volume` changes the `volume` for this song
and subsequent songs.

Specifying `loops` replays the song that many times
with -1 looping forever.""",
    "stop": """Stops the current song.""",
    "volume": """Usage: volume [level]
With no arguments, prints current volume percentage.

Otherwise, sets global volume to `level`, unless it is preceded
by a '+' or '-' sign, in which case the volume is incremented or
decremented by that amount.
Note that `level` must be between 0 and 100""",
    "ls": """Lists all songs in your music directory.
To narrow your search, see `find`.""",
    "find": """Usage: find <*substrs>
For each substring in `substrs`, lists all songs starting with that
substring in alphabetical order.""",
    "loop": """Toggles loop mode for the current song.
Note that when a new song is played, loop is automatically disabled,
so this command only takes effect when a song is playing.""",
    "time": """Shows time elapsed and time remaining for the current song.
Will print `Nothing playing` if no song is being played.""",
    "rewind": """Usage: rewind <seconds>
Rewinds the current song by `seconds`, or time elapsed,
whichever is shorter. `seconds` can either be a number or
a valid timestamp. Also applies to `forward`.

e.g. rewind 90 = rewind 1:30""",
    "forward": """Usage: forward <seconds>
Skips ahead by `seconds`, or time remaining, whichever is shorter.
`seconds` can either be a number or a valid timestamp. Also applies
to `rewind`.

e.g. forward 90 = forward 1:30""",
    "seek": """Usage: seek <seconds>
Sets the current time of the song to `seconds` after the start.
`seconds` can either be a number or a timestamp.""",
    "pause": """Toggles whether the player is paused. Like `loop`,
this only takes effect when a song is playing since the player is
unpaused whenever a song starts playing.""",
    "unpause": """Explicitly unpauses the player. Not very useful
as pause can do this too.""",
    "queue": """Usage: queue [subcommand] [*args]
This allows you to interact with the queue in various ways.
If you don't specify a subcommand, it will show all songs in the queue.
Do `list queue` to see all subcommands or `queue <subcommand>`
to see detailed help.""",
    "exit": """Exits smp. Can also use `quit`.""",
    "config": """Usage: config/config generate
With no arguments, prints out your config.
`config generate` generates a default config in ~/.config/smp/smp.conf.
WARNING: This will overwrite your existing config if you have one.""",
    "macro": """Usage: macro [subcommand] [*args]
Allows you to interact with the macro system. Macros allow you to
condense long commands or combine multiple commands into one.
If you don't specify a subcommand, it lists all created macros.
See `list macro` to see all subcommands or `macro <subcommand>
to see detailed help.""",
    "repeat": """Usage: repeat [repeats]
Repeats the current song `repeats` times, 1 by default. Repeats must
be a positive integer greater than 0. This command is effective until
the song is changed. If you are playing a queue, it will not advance
until the song stops repeating.""",
    "delete": """Usage: delete <*songs>
For each song in `songs`, deletes the song from the music directory
and removes it from all playlists it's in. Use this over your operating
system's tools for removing files or your playlists may break.""",
    "rename": """Usage: rename <song> <new_name>
Renames `song` to `new_name`, and applies this change to all playlists
it's in. Specifying the extension is not necessary, as the renamed song
will keep the existing extension. Use this over your operating system's
tools for renaming files or your playlists may break.
You can do this for as many songs as you like, e.g.
rename song1 name1 song2 name2 song3 name3 ...""",
    "exec": """Usage: exec <*scripts>
    For each script in scripts, read and execute the commands line by line.
    The scripts are processed in order, and the scripts are assumed to live at
    ~/.config/smp/scripts""",
}
