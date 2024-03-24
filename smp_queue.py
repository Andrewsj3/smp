from pygame.mixer import music
from pathlib import Path
from random import shuffle as shuf
import csv
import mutagen
from player import Player
from settings import Settings
import re
from smp_common import autocomplete, timestamp, ac_songs
from smp_help import ihelp


def should_advance():
    # checks if we should play the next song in the queue
    if not (music.get_busy() or Player.should_pause) and Player.playing_queue:
        if Player.q_idx < len(Player.queue) or Player.q_should_loop:
            return True
        else:
            Player.playing_queue = False
            return False


def queue(*args):
    if not args:
        show()
        return
    cmd, *args = args
    if cmd in Q_CMDS:
        Q_CMDS[cmd](*args)
    else:
        autocomplete(Settings.autocomplete, cmd, Q_CMDS, *args)


def num_as_position(num):
    num = str(num)
    if re.match(r"^\d*1[123]$", num):
        # Account for 11th, 12th, 13th, etc
        return num + "th"
    if num.endswith("1"):
        suffix = "st"
    elif num.endswith("2"):
        suffix = "nd"
    elif num.endswith("3"):
        suffix = "rd"
    else:
        suffix = "th"
    return num + suffix


def show():
    if Player.q_should_shuffle:
        humanized = [song[: song.index(".")] for song in Player.shuffled_queue]
    else:
        humanized = [song[: song.index(".")] for song in Player.queue]
    print(", ".join(humanized))


def find(*args):
    if Player.q_should_shuffle:
        queue = Player.shuffled_queue
    else:
        queue = Player.queue
    humanized = [song[: song.index(".")] for song in queue]
    for arg in args:
        if arg.isdigit():
            # User is searching for the nth song instead of a title
            arg = int(arg)
            if arg > len(queue) or arg < 1:
                print(f"Please enter a valid position between 1-{len(queue)}")
                continue
            idx = arg - 1
            song = queue[idx]
        else:
            song = ac_songs(Settings.autocomplete, arg)
        if not song:
            continue
        if song in queue:
            idx = queue.index(song)
            humanized[idx] = f"\x1b[5m{humanized[idx]}\x1b[25m"
            idx_as_pos = num_as_position(idx + 1)
            if len(queue) == 1:
                print(f"{Path(song).stem} is 1st in the queue")
                return
            else:
                if idx == 0:
                    next = Path(queue[idx+1]).stem
                    print(
                        f"{Path(song).stem} is 1st in the queue,"
                        f" before {next}")
                elif idx == len(queue) - 1:
                    prev = Path(queue[idx-1]).stem
                    print(
                        f"{Path(song).stem} is {idx_as_pos} in the queue,"
                        f" after {prev}")
                else:
                    next = Path(queue[idx+1]).stem
                    prev = Path(queue[idx-1]).stem
                    print(
                        f"{Path(song).stem} is {idx_as_pos} in the queue,"
                        f" before {next}, and after {prev}")
                print()
                print(f'...{", ".join(humanized[max(idx-5, 0):idx+6])}...')
        else:
            print(f"{song} is not in the queue")


def status():
    total_time = int(
        sum(
            [
                mutagen.File(Settings.music_dir / f).info.length
                for f in Player.queue
            ]
        )
    )
    cur_time = music.get_pos() / 1000 + Player.offset
    if not Player.playing_queue:
        print("Nothing playing")
        return
    else:
        time = cur_time % Player.duration
    if Player.q_should_shuffle:
        queue = Player.shuffled_queue
    else:
        queue = Player.queue
    elapsed_time = int(
        sum(
            [
                mutagen.File(Settings.music_dir / f).info.length
                for f in queue[: Player.q_idx - 1]
            ]
        )
    )
    cur_song = Path(Player.cur_song).stem
    if len(queue) == 1:
        prev_song = next_song = "N/A"
    elif Player.q_idx == 1:
        prev_song = "N/A"
        next_song = Path(queue[Player.q_idx]).stem
    elif Player.q_idx == len(queue):
        next_song = "N/A"
        prev_song = Path(queue[Player.q_idx-2]).stem
    else:
        next_song = Path(queue[Player.q_idx]).stem
        prev_song = Path(queue[Player.q_idx-2]).stem

    print(f"Previous song: {prev_song}, next song: {next_song}")
    print(f"Currently playing {cur_song} ({Player.q_idx}/{len(queue)})")
    print(f"Total length of playlist: {timestamp(total_time)}")
    print(
        f"Total time elapsed: {timestamp(int(elapsed_time + time))} "
        f"({100*((elapsed_time + time)/total_time):.1f}%)"
    )


def clear():
    Player.q_idx = 0
    Player.queue.clear()
    Player.shuffled_queue.clear()
    Player.playing_queue = False
    # Bad things would happen if we tried to advance and the queue was suddenly empty


def add(*args):
    if not args:
        ihelp("queue add")
        return
    for arg in args:
        song = ac_songs(Settings.autocomplete, arg)
        if song:
            if song in Player.queue:
                print("That song is already in the queue")
                return
            Player.queue.append(song)
            Player.shuffled_queue.append(song)


def qnext():
    if not Player.playing_queue:
        if not Player.queue:
            print("Nothing queued")
        else:
            print("Either end of queue already reached or nothing playing")
    else:
        music.stop()
        music.unload()
        Player.playing_queue = False
        play()


def prev():
    if not Player.playing_queue:
        if not Player.queue:
            print("Nothing queued")
        else:
            print("Either end of queue already reached or nothing playing")
    elif Player.q_idx > 1:
        Player.q_idx -= 2
        play()
    else:
        print("Can't go back any further")


def loop():
    Player.q_should_loop ^= True
    print(f"Queue loop: {'on' if Player.q_should_loop else 'off'}")


def randomize():
    if not Player.shuffled_queue:
        print("Nothing to randomize")
        return
    elif len(Player.shuffled_queue) == 1:
        print("Still nothing to randomize")
        return
    initial = [*Player.shuffled_queue]
    while Player.shuffled_queue == initial:
        shuf(Player.shuffled_queue)
    Player.q_should_shuffle = True


def shuffle():
    Player.q_should_shuffle ^= True
    if Player.queue == Player.shuffled_queue:
        randomize()


def play():
    if not Player.queue:
        print("Nothing in the queue")
        return
    if Player.q_idx == len(Player.queue):
        Player.q_idx = 0
        if Player.q_should_shuffle:
            randomize()
    Player.playing_queue = True
    if not Player.q_should_shuffle:
        Player.cur_song = Settings.music_dir / Player.queue[Player.q_idx]
    else:
        Player.cur_song = (
            Settings.music_dir / Player.shuffled_queue[Player.q_idx]
        )
    song = Player.cur_song
    music.load(song)
    Player.loops = 0
    Player.offset = 0
    Player.should_pause = False
    file = mutagen.File(song)
    Player.duration = file.info.length
    music.play()
    if Player.q_idx < len(Player.queue):
        Player.q_idx += 1


def save(*args):
    if not args:
        print("Expected a name")
        return
    file = args[0]
    with open(f"{Settings.playlist_dir}/{file}.csv", "w", newline="") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(Player.queue)


def load(*args):
    if not args:
        print("Playlists:")
        for f in Settings.playlist_dir.glob("*"):
            print(f.stem)
        return
    file = args[0]
    if not Path.exists(Path(f"{Settings.playlist_dir}/{file}.csv")):
        print("That playlist doesn't exist")
        return
    with open(f"{Settings.playlist_dir}/{file}.csv", "r", newline="") as f:
        reader = csv.reader(f, delimiter=",")
        Player.queue = next(iter(reader))
        Player.shuffled_queue = [*Player.queue]


def remove(*args):
    for arg in args:
        arg = ac_songs(Settings.autocomplete, arg)
        if arg in Player.queue:
            idx = Player.queue.index(arg)
            Player.queue.remove(arg)
            Player.shuffled_queue.remove(arg)
            if Player.playing_queue and idx < Player.q_idx:
                Player.q_idx -= 1
        else:
            print("That song is not in the queue")


def swap(*args):
    if len(args) % 2 != 0:
        print("Expected an even number of arguments")
        return
    for i in range(0, len(args), 2):
        first, second = args[i], args[i + 1]
        if first in Player.queue and second in Player.queue:
            idx1, idx2 = Player.queue.index(first), Player.queue.index(second)
            Player.queue[idx1], Player.queue[idx2] = (
                Player.queue[idx2],
                Player.queue[idx1],
            )
        else:
            first = ac_songs(Settings.autocomplete, first)
            second = ac_songs(Settings.autocomplete, second)
            if first and second:
                idx1, idx2 = (
                    Player.queue.index(first),
                    Player.queue.index(second),
                )
                Player.queue[idx1], Player.queue[idx2] = (
                    Player.queue[idx2],
                    Player.queue[idx1],
                )


Q_CMDS = {
    "add": lambda *args: add(*args),
    "clear": lambda *args: clear(),
    "remove": lambda *args: remove(*args),
    "play": lambda *args: play(),
    "next": lambda *args: qnext(),
    "prev": lambda *args: prev(),
    "find": lambda *args: find(*args),
    "loop": lambda *args: loop(),
    "swap": lambda *args: swap(*args),
    "shuffle": lambda *args: shuffle(),
    "randomize": lambda *args: randomize(),
    "save": lambda *args: save(*args),
    "load": lambda *args: load(*args),
    "status": lambda *args: status(),
}
