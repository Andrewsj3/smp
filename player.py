from pathlib import Path
import mutagen


class Player:
    # Global settings for the music player
    volume = 100
    loops = 0
    repeats = 0
    offset = 0
    duration = 0
    queue = []
    queue_info = {}
    macros = {}
    cur_song = Path()
    shuffled_queue = []
    playing_queue = False
    should_pause = False
    q_idx = 0
    q_should_loop = False
    q_should_shuffle = False
    awaiting_commands = True

    @classmethod
    def update_info(cls, song, settings):
        cls.queue_info[song] = int(mutagen.File(
            settings.music_dir / song).info.length)
