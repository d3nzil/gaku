"""Validates various answers for test questions."""

import logging

import gaku
import gaku.api_types
import gaku.database
import gaku.card_types
import gaku.question
from gaku.card_types import VocabCard

import pytest
from .utils import TestSetup, get_answer_for_question


class TestAnswering(TestSetup):
    """Validates various answers for test questions."""

    def test_answer_with_three_dots(self) -> None:
        """Verifies that valid answers are for answers ending with "...".

        The accepted answers are:
        - with ...
        - without ... (and no space required at the end)

        """

        test_card = gaku.card_types.RadicalCard(
            writing="card with ... answer suffix",
            reading="kana",
            # there is space since I seen such entry in dictionary
            meanings=[gaku.question.AnswerText(answer_text="test ...")],
        )

        logging.info("Creating cards and adding FSRS recors")
        manager = self.manager
        manager.db.add_cards([test_card])

        test_setup = gaku.api_types.StartTestRequest()

        logging.info("Validating answer with ...")
        manager.start_test_session_new_cards(test_setup)
        test = manager.test_session
        assert test is not None

        question = test.get_test_question()
        answers = get_answer_for_question(question)
        result = test.answer_question(answers)
        assert result.all_correct is True

        manager.start_test_session_new_cards(test_setup)

        logging.info("Validating answer without ...")
        # cleanup fsrs, so the card is new again
        manager.db.delete_card_fsrs(test_card.card_id)

        manager.start_test_session_new_cards(test_setup)
        test = manager.test_session
        assert test is not None

        question = test.get_test_question()
        answers = get_answer_for_question(question)
        # remove the ... from answer
        for key, value in answers.items():
            if value.endswith("..."):
                answers[key] = "test"
                break
        logging.info(f"Answers without ... are: {answers}")

        result = test.answer_question(answers)
        assert result.all_correct is True


    def test_answering_得る(self) -> None:
        """Verifies that vocab card with one dictionary entry is
        generated correctly.
        """
        test_vocab = "得る"
        manager = self.manager

        generated_imports = manager.generate_vocab_import([test_vocab])
        logging.info(f"Generated cards for {test_vocab} are: {generated_imports}")
        vocab_cards = [
            card
            for card in generated_imports.generated_cards.values()
            if isinstance(card, VocabCard)
        ]
        logging.debug(f"Vocab cards: {vocab_cards}")
        assert len(vocab_cards) == 2
        for c in vocab_cards:
            if c.dictionary_id == 1588760:
                card = c
                break
        else:
            pytest.fail("No matching card found")
        manager.db.add_cards([card])

        test_setup = gaku.api_types.StartTestRequest()

        logging.info("Validating answer with ...")
        manager.start_test_session_new_cards(test_setup)
        test = manager.test_session
        assert isinstance(test, gaku.test_session.TestSession)

        while True:
            question = test.get_test_question()
            assert isinstance(question, gaku.api_types.NextCardMessage)
            if question.next_question is None:
                break
            logging.warning(question.next_question)
            answers = get_answer_for_question(question)
            logging.warning(answers)
            result = test.answer_question(answers)
            logging.warning(f"Answer response {result}")
            assert result.all_correct

        assert result.all_correct is True


