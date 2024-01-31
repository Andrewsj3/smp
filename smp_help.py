def ihelp(*topic):
    if topic:
        topic = " ".join(topic)
        if topic.startswith("queue") and len(topic.split()) == 2:
            _, subcmd = topic.split()
            print(Q_CMDS.get(subcmd, "No help for that"))
        else:
            print(CMDS.get(topic, "No help for that"))
        return
    print("Welcome to smp's interactive help utility!")
    print("Type `quit` or Ctrl-D to return to smp")
    print("Type `list` to see the list of available commands")
    print("Type `list queue` to see the list of queue subcommands")
    while True:
        try:
            name = input(">>> ").lower().strip()
        except EOFError:
            print()
            return
        if not name:
            continue
        if name == "quit":
            return
        elif name == "list":
            print("\n".join(CMDS))
        elif name == "list queue":
            print("\n".join(Q_CMDS))
        elif name.startswith("queue") and len(name.split()) == 2:
            _, subcmd = name.split()
            print(Q_CMDS.get(subcmd, "No help for that"))
        else:
            print(CMDS.get(name, "No help for that"))


Q_CMDS = {
    "add": """Usage: queue add <*songs>
Adds songs to the end of the queue. Every argument after `add`
is treated as a song. Works with autocomplete.""",
    "clear": """Clears the current queue.""",
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
    "status": """Shows the current song being played, the total
length of the playlist, and total time elapsed as a timestamp
and a percentage. Only works if the queue is playing (paused is ok).""",
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

Otherwise, sets global volume to `level`.
Note that `level` must be between 0 and 100""",
    "ls": """Usage: ls [-s <substr>] [-n <range>]
With no arguments, lists all songs in the music directory.

With `-s`, lists only songs beginning with `substr`.

With `-n`, lists only songs which indexes are in `range`.
The syntax is `start`,`stop`,`step`, just like range.
e.g. `ls -n 0,10,2` lists every other song in the first 10 songs.

These flags can be specified multiple times and are applied
from left to right.""",
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
    "macro": """Usage: macro <name> <*args>
Creates a new macro called `name`, that when invoked, expands
to `args`. You can use this to combine multiple commands into one,

e.g. macro my-macro queue load my-playlist; queue shuffle; queue play

Note that semicolons are required to separate commands. You can also
add arguments after macros as if they were normal commands, e.g.
 macro add queue add
 add my-song -> queue add my-song""",
    "repeat": """Usage: repeat [repeats]
Repeats the current song `repeats` times, 1 by default. Repeats must
be a positive integer greater than 0. This command is effective until
the song is changed. If you are playing a queue, it will not advance
until the song stops repeating.""",
}
