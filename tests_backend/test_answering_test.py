"""Validates various answers for test questions."""

import logging

import gaku
import gaku.api_types
import gaku.database
import gaku.card_types
import gaku.question

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
        assert result is True

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
        assert result is True
