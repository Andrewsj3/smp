from settings import Settings


class Player:
    # Global settings for the music player
    volume = Settings.default_volume
    loops = 0
    repeats = 0
    offset = 0
    duration = 0
    queue = []
    macros = {}
    cur_song = ""
    shuffled_queue = []
    playing_queue = False
    should_pause = False
    q_idx = 0
    q_should_loop = False
    q_should_shuffle = False
    history_idx = 0
    history_picked = False  # Whether the most recent input was
    # selected from history
