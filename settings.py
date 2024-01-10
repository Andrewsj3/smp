from pathlib import Path

class Settings:
    music_dir: lambda f: Path(f).expanduser() = "~"
    playlist_dir: lambda f: Path(f).expanduser() = "~"
    # Changed to ~ to ensure directory exists as invalid directory would
    # make the program crash on startup. if this still crashes,
    # you have bigger problems
    prompt: str = " "
    autocomplete: int = 1
    default_volume: float = 80
    ls_sep: str = ", "
    _cfg_dict = {}

    @classmethod
    def read_config(cls, cfg_dict, startup=True):
        for key in cfg_dict:
            cls._cfg_dict[key] = cfg_dict[key]
        attrs = [i for i in dir(cls) if "__" not in i][1:-1]
        for attr in attrs:
            type_ = cls.__annotations__[attr]
            try:
                new_val = cls._cfg_dict[attr]
            except KeyError:
                config(generate=True)
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
