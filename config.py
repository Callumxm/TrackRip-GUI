import json
import os

CONFIG_DIR = os.path.expanduser("~/.config/trackrip")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "save_location": "~/Music",
    "quality": "320",
    "default_album": "Singles",
}


def load_config():
    config = DEFAULT_CONFIG.copy()

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as file:
                saved_config = json.load(file)

            config.update(saved_config)

        except (json.JSONDecodeError, OSError) as e:
            print(f"Could not load config: {e}")

    return config


def save_config(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)

    temp_file = f"{CONFIG_FILE}.tmp"

    try:
        with open(temp_file, "w") as file:
            json.dump(
                config,
                file,
                indent=4,
            )
            file.flush()
            os.fsync(file.fileno())

        os.replace(temp_file, CONFIG_FILE)

    except OSError as e:
        print(f"Could not save config: {e}")

        if os.path.exists(temp_file):
            os.remove(temp_file)

        raise
