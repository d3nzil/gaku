"""Verifies dictionary related functionality."""

import logging

import pytest
from gaku.dictionary import JapaneseDictionary

from .utils import RESOURCE_DIR


VOCAB_DICTIONARY = JapaneseDictionary(RESOURCE_DIR / "JMdict_e.xml")


class TestVocabDictionary:
    """Verify correct functionality of Vocab dictionary."""

    @pytest.mark.slow
    def test_get_meanings_of_得る(self) -> None:
        """Verifies that 得る meanings are read correctly from the xml file.
        Based on bug where this was incorrectly imported into card.
        """

        dictionary = VOCAB_DICTIONARY
        entries = dictionary.get_vocabulary_by_kanji("得る")
        logging.info(f"Entries obtained from dictionary: {entries}")

        entry = [entry for entry in entries if entry.ent_seq == 1588760]
        assert len(entry) == 1
        meanings = [
            meaning
            for vocab_meaning in entry[0].meanings
            for meaning in vocab_meaning.meanings
        ]
        logging.info(f"Extracted meanings: {meanings}")

        expected_meanings = [
            # 1. meaning set
            "to get",
            "to earn",
            "to acquire",
            "to procure",
            "to gain",
            "to secure",
            "to attain",
            "to obtain",
            "to win",
            # 2. meaning set
            "to understand",
            "to comprehend",
            # 3. meaning set
            "to receive something undesirable (e.g. a punishment)",
            "to get (ill)",
            # 4. meaning set - this one is as one line in dictionary,
            # so it can be a bit confusing
            "to be able to ..., can ...",
        ]

        assert set(meanings) == set(expected_meanings)
