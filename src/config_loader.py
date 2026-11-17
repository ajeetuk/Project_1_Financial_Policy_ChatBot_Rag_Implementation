from functools import lru_cache
from pathlib import Path

import yaml

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "config.yaml"


@lru_cache(maxsize=1)
def load_config() -> dict:
    """Read config/config.yaml once and return it as a dictionary."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)