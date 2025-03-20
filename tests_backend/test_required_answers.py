"""Verified required answers functionality."""

import logging

from gaku.card_types import (
    KanjiCard,
    RadicalCard,
    AnswerText,
)
from gaku.api_types import StartTestRequest

from .utils import TestSetup, get_answer_for_question

KANJI_CARD_REQUIRED = KanjiCard(
    writing="kanji writing",
    radical_id=987654,
    on_readings=[
        AnswerText(answer_text="kanji on reading", required=True),
        AnswerText(answer_text="another answer", required=True),
        AnswerText(answer_text="not required"),
    ],
    kun_readings=[AnswerText(answer_text="kanji kun reading", required=False)],
    meanings=[
        AnswerText(answer_text="kanji meanings", required=True),
        AnswerText(answer_text="also required", required=True),
    ],
)
NUM_KANJI_REQUIRED_ANSWERS_ON = 2
NUM_KANJI_REQUIRED_ANSWERS_KUN = 0
NUM_KANJI_REQUIRED_ANSWERS_MEANINGS = 2

RADICAL_CARD_NO_REQUIRED = RadicalCard(
    writing="radical writing",
    reading="radical reading",
    meanings=[
        AnswerText(answer_text="radical meaning", required=False),
        AnswerText(answer_text="another meaning", required=False),
    ],
)


class TestBasics(TestSetup):
    """Test for basic functionality of Gaku."""

    def test_num_required_answers(self) -> None:
        """Verifies the number of required answers info is correctly generated.

        Verifies
        - 2/all required
        - 1 answer (no required, singular)
        - all/all required
        """
        manager = self.manager

        manager.db.add_card(KANJI_CARD_REQUIRED)

        test_setup = StartTestRequest(num_cards=0, generate_extra_questions=False)
        manager.start_test_session(test_setup)
        test = manager.test_session
        assert test is not None

        question = test.get_test_question()
        while question.next_question is not None:
            for answer_group in question.next_question.answers:
                for answer in answer_group.answers:
                    logging.info(
                        f"Answer header is: {answer.header}, num header: {answer.header_num_questions}"
                    )
                    if "on".casefold() in answer.header.casefold():
                        logging.info("Checking On reading")
                        assert (
                            answer.header_num_questions
                            == f", {NUM_KANJI_REQUIRED_ANSWERS_ON}/{len(answer.answers)} required"
                        )
                    if "kun".casefold() in answer.header.casefold():
                        logging.info("Checking Kun reading")
                        assert (
                            answer.header_num_questions
                            == f", {len(answer.answers)} answer"
                        )
                    if "meaning".casefold() in answer.header.casefold():
                        logging.info("Checking On reading")
                        assert (
                            answer.header_num_questions
                            == f", {NUM_KANJI_REQUIRED_ANSWERS_MEANINGS}/{len(answer.answers)} required"
                        )

            answer_response = test.answer_question(get_answer_for_question(question))
            assert answer_response.all_correct is True
            question = test.get_test_question()

    def test_no_required_answers(self) -> None:
        """Verifies the number of required answers info is correctly generated.

        Verifies
        - multiple answers, not required: num answers
        - default for required is False
        """
        manager = self.manager

        manager.db.add_card(RADICAL_CARD_NO_REQUIRED)

        test_setup = StartTestRequest(num_cards=0, generate_extra_questions=False)
        manager.start_test_session(test_setup)
        test = manager.test_session
        assert test is not None

        question = test.get_test_question()
        assert question.next_question is not None

        answer_groups = question.next_question.answers
        for answer_group in answer_groups:
            for answer in answer_group.answers:
                if "meaning".casefold() in answer.header.casefold():
                    assert (
                        answer.header_num_questions
                        == f", {len(answer.answers)} answers"
                    )

                if "reading".casefold() in answer.header.casefold():
                    assert (
                        "required".casefold()
                        not in answer.header_num_questions.casefold()
                    )
