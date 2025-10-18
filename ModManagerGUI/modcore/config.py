import os
import json
import shutil
import sys
from dataclasses import dataclass

@dataclass
class Config:
    GameInstallDir: str | None = None


class ConfigIO:

    @staticmethod
    def get_application_path() -> str:
        """
        Return the directory where the current process executable/script lives.
        """
        if getattr(sys, "frozen", False):  # PyInstaller bundled
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.realpath(__file__))

    @staticmethod
    def get_config_dir() -> str:
        """Return a writable config directory."""
        # Inside Flatpak/AppImage: use user config
        base = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        cfg_dir = os.path.join(base, "wotmodassistant")
        os.makedirs(cfg_dir, exist_ok=True)
        return cfg_dir

    @staticmethod
    def get_config_path() -> str:
        """Full path to config.json in writable location."""
        return os.path.join(ConfigIO.get_config_dir(), "config.json")

    @staticmethod
    def write_config(config: Config):
        path = ConfigIO.get_config_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config.__dict__, f, indent=4)

    @staticmethod
    def read_config() -> Config | None:
        path = ConfigIO.get_config_path()
        if not os.path.isfile(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Config(**data)
    
    @staticmethod
    def get_extract_folder() -> str:
        base_cache = os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))
        extract_dir = os.path.join(base_cache, "wotmodassistant", "extract")
        os.makedirs(extract_dir, exist_ok=True)
        return extract_dir

    @staticmethod
    def clear_extract_folder():
        extract_dir = ConfigIO.get_extract_folder()
        # remove all subdirectories
        for subdir in os.listdir(extract_dir):
            full_path = os.path.join(extract_dir, subdir)
            if os.path.isdir(full_path):
                shutil.rmtree(full_path)
            else:
                os.remove(full_path)

    @staticmethod
    def get_mods_folder_path() -> str:
        config = ConfigIO.read_config()
        if config is None or config.GameInstallDir is None:
            raise Exception("Config file not found or missing GameInstallDir")
        return os.path.join(config.GameInstallDir, "mods")

    @staticmethod
    def dump_config() -> str:
        path = ConfigIO.get_config_path()
        if not os.path.isfile(path):
            return "Config file not found"
        with open(path, "r") as f:
            return f.read()
