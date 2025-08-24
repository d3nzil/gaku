"""User configuration related functionality."""

import json
import logging
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


CONFIG_PATH: Optional[Path] = None


class GakuConfig(BaseModel):
    """Gaku configuration."""

    # test settings
    num_default_cards_to_study: int = 10
    num_current_questions: int = 7
    num_required_answers: int = 1
    num_repeats_after_mistake: int = 2
    generate_extra_questions: bool = True
    radicals_test_meaning: bool = True
    generate_kanji_for_vocab: bool = True
    generate_radicals_for_kanji: bool = True


    def to_json(self) -> dict:
        """Convert Gaku configuration to JSON format.

        Returns
        -------
        dict
            Gaku configuration in JSON format.
        """
        return self.model_dump(mode="json")


CONFIG: GakuConfig = GakuConfig()


def get_config() -> GakuConfig:
    """Get Gaku configuration.

    Returns
    -------
    GakuConfig
        Gaku configuration.
    """
    return CONFIG


def set_config(updated_config: GakuConfig) -> None:
    """Updates current Gaku configuration.

    Parameters
    ----------
    config: GakuConfig
        The updated configuration
    """
    global CONFIG
    CONFIG = updated_config
    if CONFIG_PATH is not None:
        save_config(CONFIG_PATH)
    else:
        logging.warning("Config path not set, Gaku configuration will not be saved")


def set_config_path(config_path: Path) -> None:
    """Sets location for the configuration.

    config_path: Path
        The path to the config file including the filename.
    """
    global CONFIG_PATH
    CONFIG_PATH = config_path


def load_config(config_path: Path) -> None:
    """Load Gaku configuration.

    Parameters
    ----------
    config_path : Path
        Path to the configuration file.
    """
    global CONFIG
    with open(config_path, "r") as f:
        CONFIG = GakuConfig(**json.load(f))


def save_config(config_path: Path) -> None:
    """Save Gaku configuration.

    Parameters
    ----------
    config_path : Path
        Path to the configuration file.
    """
    with open(config_path, "w") as f:
        json.dump(CONFIG.to_json(), f, indent=4)
