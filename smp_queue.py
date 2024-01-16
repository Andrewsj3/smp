from pygame.mixer import music
from pathlib import Path
from random import shuffle as shuf
import csv
import mutagen
from player import Player
from settings import Settings
from smp_common import *


def should_advance():
    # checks if we should play the next song in the queue
    if not (music.get_busy() or Player.should_pause) and Player.playing_queue:
        if Player.q_idx < len(Player.queue):
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


def show():
    if Player.q_should_shuffle:
        humanized = [song[: song.index(".")] for song in Player.shuffled_queue]
        print(", ".join(humanized))
    else:
        humanized = [song[: song.index(".")] for song in Player.queue]
        print(", ".join(humanized))


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
    if Player.cur_song.name in Player.queue[Player.q_idx - 1]:
        queue = Player.queue
    else:
        queue = Player.shuffled_queue
    elapsed_time = int(
        sum(
            [
                mutagen.File(Settings.music_dir / f).info.length
                for f in queue[: Player.q_idx - 1]
            ]
        )
    )
    cur_song = Path(Player.cur_song).name
    cur_song = cur_song[: cur_song.rindex(".")]
    print(f"Currently playing {cur_song}")
    print(f"Total length of playlist: {timestamp(total_time)}")
    print(
        f"Total time elapsed: {timestamp(int(elapsed_time + time))} "
        f"({100*((elapsed_time + time)/total_time):.1f}%)"
    )


def clear():
    Player.q_idx = 0
    Player.queue.clear()
    Player.shuffled_queue.clear()


def add(*args):
    files = gen_files()
    for arg in args:
        if arg in files:
            Player.queue.append(arg)
            Player.shuffled_queue.append(arg)
        else:
            file = ac_songs(Settings.autocomplete, arg)
            if file:
                Player.queue.append(file)
                Player.shuffled_queue.append(file)


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
    if Player.q_idx > 1:
        Player.q_idx -= 2
        play()
    elif Player.q_idx == 0:
        Player.q_idx = len(Player.queue) - 2
        play()


def loop():
    Player.q_should_loop ^= True


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
    else:
        if not Player.q_should_loop:
            Player.playing_queue = False
        Player.q_idx = 0


def save(file):
    with open(f"{Settings.playlist_dir}/{file}.csv", "w", newline="") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(Player.queue)


def load(file):
    if not Path.exists(Path(f"{Settings.playlist_dir}/{file}.csv")):
        print("That playlist doesn't exist")
        return
    with open(f"{Settings.playlist_dir}/{file}.csv", "r", newline="") as f:
        reader = csv.reader(f, delimiter=",")
        Player.queue = next(iter(reader))
        Player.shuffled_queue = [*Player.queue]


def remove(*args):
    for arg in args:
        if arg in Player.queue:
            Player.queue.remove(arg)
            Player.shuffled_queue.remove(arg)
        else:
            if (song := ac_songs(Settings.autocomplete, arg)) in Player.queue:
                Player.queue.remove(song)
                Player.shuffled_queue.remove(song)


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
            second = ac_songs(Setting.autocomplete, second)
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
    "clear": lambda: clear(),
    "remove": lambda *args: remove(*args),
    "play": lambda: play(),
    "next": lambda: qnext(),
    "prev": lambda: prev(),
    "loop": lambda: loop(),
    "swap": lambda *args: swap(*args),
    "shuffle": lambda: shuffle(),
    "randomize": lambda: randomize(),
    "save": lambda *args: save(*args),
    "load": lambda *args: load(*args),
    "status": lambda: status(),
}
