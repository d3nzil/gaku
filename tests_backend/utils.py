"""Test related utilities."""

import logging
import tempfile
from pathlib import Path
from shutil import copy
from typing import Generator

import gaku
import gaku.db_dictionary
import gaku.dictionary
import pytest

REPO_ROOT = Path(__file__).parent.parent
RESOURCE_DIR = REPO_ROOT / "resources"
TEST_DATA: Path = Path(__file__).parent / "test-data"
TEST_DATA.mkdir(exist_ok=True)


class TestSetup:
    """Test setup."""

    tempdir: Path
    manager: gaku.GakuManager
    dictionary_file = TEST_DATA / "dictionary.db"

    @pytest.fixture(autouse=True)
    def setup_teardown(self) -> Generator:
        """Sets up the test environment and tears it down after test ends."""
        self.tempdir = Path(tempfile.mkdtemp())

        if not self.dictionary_file.exists():
            self._setup_dictionary()
        copy(self.dictionary_file, self.tempdir / "dictionary.db")

        self.manager = gaku.GakuManager(
            userdata_dir=self.tempdir,
            resource_dir=RESOURCE_DIR,
            gaku_root_dir=REPO_ROOT,
        )

        yield
        # no teardown needed for now

    def _setup_dictionary(self) -> None:
        """(Re-)Creates dictionary if current is older than 24hours."""

        if self.dictionary_file.exists():
            return

        dictionary = gaku.db_dictionary.DictionaryManager(
            f"sqlite:///{str(self.dictionary_file.resolve())}"
        )
        dictionary.create_database()

        # import the dictionaries
        logging.info("Importing dictionaries, this might take a few minutes")
        radical_dict = gaku.dictionary.RadicalDictionary(
            RESOURCE_DIR / "kanji-radicals.csv"
        )
        kanji_dict = gaku.dictionary.KanjiDictionary(RESOURCE_DIR / "kanjidic2.xml")
        japanese_dict = gaku.dictionary.JapaneseDictionary(
            RESOURCE_DIR / "JMdict_e.xml"
        )
        ono_dict = gaku.dictionary.load_ono_dictionary(RESOURCE_DIR / "j-ono-data.json")
        dictionary.add_radicals(list(radical_dict.radicals.values()))
        dictionary.add_kanji(list(kanji_dict.kanji.values()))
        dictionary.add_vocabulary(list(japanese_dict.entries.values()))
        dictionary.add_onomatopoeia(ono_dict)
        logging.info("Finished importing dictionaries")


def get_answer_for_question(question: gaku.api_types.NextCardMessage) -> dict[str, str]:
    """Creates correct answers for current question.

    Parameters
    ----------
    question : gaku.api_types.NextCardMessage
        The question data to answer

    Returns
    -------
    dict
        Correct answers

    Raises
    ------
        ValueError if there is no question.
    """
    if question.next_question is None:
        raise ValueError("No question to answer")

    question_data = question.next_question
    response = {
        answer.answer_id: ",".join([ans.answer_text for ans in answer.answers])
        for answer_group in question_data.answers
        for answer in answer_group.answers
    }
    return response
