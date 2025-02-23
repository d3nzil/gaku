"""User configuration related functionality."""

import json
from pathlib import Path
from typing import Optional


class GakuConfig:
    """Gaku configuration."""

    def __init__(self, config: Optional[dict] = None) -> None:
        """Initialize Gaku configuration.

        Parameters
        ----------
        config : dict
            Gaku configuration.
        """
        if config is None:
            config = {}

        # test settings
        self.num_default_cards_to_study: int = config.get(
            "num_default_cards_to_study", 10
        )
        self.num_current_questions: int = config.get("num_current_cards", 7)
        self.required_answers: int = config.get("required_answers", 1)
        self.repeats_after_mistake: int = config.get("repeats_after_mistake", 2)
        self.practice_radicals_for_kanji: bool = config.get(
            "practice_radicals_for_kanji", True
        )
        self.practice_kanji_for_words: bool = config.get(
            "practice_kanji_for_words", True
        )
        self.radicals_test_meaning: bool = config.get("radicals_test_meaning", True)

    def to_json(self) -> dict:
        """Convert Gaku configuration to JSON format.

        Returns
        -------
        dict
            Gaku configuration in JSON format.
        """
        return {
            "required_answers": self.required_answers,
            "repeats_after_mistake": self.repeats_after_mistake,
            "practice_radicals_for_kanji": self.practice_radicals_for_kanji,
            "practice_kanji_for_words": self.practice_kanji_for_words,
        }


CONFIG: GakuConfig = GakuConfig()


def get_config() -> GakuConfig:
    """Get Gaku configuration.

    Returns
    -------
    GakuConfig
        Gaku configuration.
    """
    return CONFIG


def load_config(config_path: Path) -> None:
    """Load Gaku configuration.

    Parameters
    ----------
    config_path : Path
        Path to the configuration file.
    """
    global CONFIG
    with open(config_path, "r") as f:
        CONFIG = GakuConfig(json.load(f))


def save_config(config_path: Path) -> None:
    """Save Gaku configuration.

    Parameters
    ----------
    config_path : Path
        Path to the configuration file.
    """
    with open(config_path, "w") as f:
        json.dump(CONFIG.to_json(), f, indent=4)
