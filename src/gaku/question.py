"""Test questions related functionality."""

import logging
import re
import uuid
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, computed_field


class AnswerType(Enum):
    """Answer type."""

    ROMAJI = "ROMAJI"
    HIRAGANA = "HIRAGANA"
    KATAKANA = "KATAKANA"
    KANA = "KANA"  # TODO: check if this or hiragana should be removed


class AnswerText(BaseModel):
    """Answer text and information if this answer is required."""

    answer_text: str
    required: bool = False


TestAnswer = dict[str, str]
"""Dictionary containing answers for a test question

- keys are question ids
- values are comma separated answers for the question with matching id
"""


class Answer(BaseModel):
    """Answer for the test card."""

    answer_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    answer_type: AnswerType
    answers: list[AnswerText]
    header: str
    # header_num_questions: str = ""
    hint: Optional[str] = None
    note: Optional[str] = None
    font_size: float = 1.0

    @computed_field  # type:ignore[misc]
    @property
    def header_num_questions(self) -> str:
        """Adds number of required answers to header."""
        logging.info("Getting num questions header")

        num_required_answers = get_num_required_answers(self.answers)
        num_answers_total = len(self.answers)
        if num_required_answers > 0:
            required_answers = f", {num_required_answers}/{num_answers_total} required"
        else:
            if num_answers_total == 1:
                required_answers = f", {num_answers_total} answer"
            else:
                required_answers = f", {num_answers_total} answers"
        return required_answers

    def prepare_answer(self, answer_text: str) -> str:
        """Does necessary processing of answer text
        (e.g converting all comma types to same comma).

        Parameters
        ----------
        answer_text: str
            Text for single answer.

        Returns
        -------
        str
            processed answer text
        """
        # first replace japanese commas with english comma
        japanese_commas = ["、", "，"]
        for japanese_comma in japanese_commas:
            answer_text = answer_text.replace(japanese_comma, ",")
        # replace dashes to the character used in dictionary
        dashes = ["ー", "~", "〜", "-"]
        for dash in dashes:
            answer_text = answer_text.replace(dash, "-")

        # casefold the text to ensure there are no case problems when comparing
        answer_text = answer_text.casefold()

        # not stripping text, since it might need to be split first

        return answer_text

    def get_required_answers(self) -> list[str]:
        """Creates a list of required answers
        and prepares the text for checking.

        Returns
        -------
        list[str]
            List of required answers text.
        """
        required_answers: list[str] = []
        for answer in self.answers:
            if answer.required:
                required_answers.append(self.prepare_answer(answer.answer_text))

        return required_answers

    def check_answer(self, user_answers: TestAnswer) -> tuple[bool, list[str]]:
        """Check if the answer is correct.

        Parameters
        ----------
        answers : dict[str, str]
            Dictionary with the answers.

        Returns
        -------
        bool
            True if the answer is correct, False otherwise.
        """

        # check if the answer_id is in the user's answers
        if self.answer_id not in user_answers:
            logging.warning(
                f"This answer id {self.answer_id} was not found in answers: {user_answers}"
            )
            return False, []

        user_answer = user_answers[self.answer_id]
        user_answer = self.prepare_answer(user_answer)
        # if there is comma in the user's answer, split it and check each part
        received_answers = set([answer.strip() for answer in user_answer.split(",")])
        logging.info(f"Processed received answers: {received_answers}")

        # if the type is ROMAJI, we need to preprocess the answer
        if self.answer_type == AnswerType.ROMAJI:
            logging.debug("Processing Romaji answer type")
            # create a set of correct answers
            expected_answers = set(
                [self.prepare_answer(answer.answer_text) for answer in self.answers]
            )
            required_answers = set(self.get_required_answers())

            # we want to accept anwers with the text in parentheses missing
            # remove text in parentheses for each answer in self.answers
            # the parenthesis can be in the beginning or at the end of the answer
            # so the best solution is probably using regex to find what to remove
            paren_regex = re.compile(r"\s*\([^)]*\)\s*")
            no_paren_answers = [
                paren_regex.sub("", answer).strip() for answer in expected_answers
            ]
            no_paren_required_answers: list[str] = [
                paren_regex.sub("", required_answer).strip()
                for required_answer in required_answers
            ]
            expected_answers.update(no_paren_answers)
            required_answers.update(no_paren_required_answers)
            logging.debug(f"Accepted answers - paren: {expected_answers}")
            logging.debug(f"Required answers - paren: {required_answers}")

            remove_suffixes = ["..."]
            no_suffix_answers = []
            for suffix in remove_suffixes:
                for answer_text in expected_answers:
                    if answer_text.endswith(suffix):
                        no_suffix_answers.append(answer_text[0 : -len(suffix)].strip())
                        break
            expected_answers.update(no_suffix_answers)

            no_suffix_required_answers = []
            for suffix in remove_suffixes:
                for answer_text in required_answers:
                    if answer_text.endswith(suffix):
                        no_suffix_required_answers.append(
                            answer_text[0 : -len(suffix)].strip()
                        )
                        break
            required_answers.update(no_suffix_required_answers)
            logging.debug(f"Accepted answers - suffix: {expected_answers}")
            logging.debug(f"Required answers - suffix: {required_answers}")

            # verify all required answers are present
            if required_answers - received_answers:
                logging.info("Not all required answers present")
                logging.info(f"Required: {required_answers}")
                logging.info(f"Provided: {received_answers}")
                return False, list(received_answers - expected_answers)

            # check if all the answers are in the set of correct answers
            # since we are using set, the order of answers does not matter
            # and we can just check if the set of received answers is a subset of the set of correct answers
            answer_is_correct = received_answers.issubset(expected_answers)
            if not answer_is_correct:
                logging.info(
                    f"Answer is not correct, accepted answers are: {expected_answers}"
                )

            # validate there were no dulicate answers
            if len(received_answers) != len(user_answer.split(",")):
                logging.info("Duplicate answers")
                return False, list(received_answers - expected_answers)

            return answer_is_correct, list(received_answers - expected_answers)

        logging.debug("Processing Hiragana or Katakana answer")
        # if the type is HIRAGANA or KATAKANA we need to split the answer to set

        # first replace japanese commas with english commas
        # using casefold just to be consistent with the ROMAJI type
        # but should not be necessary here as we are comparing kana
        expected_answers = set()
        for answer in self.answers:
            answer_text = self.prepare_answer(answer.answer_text)
            expected_answers.update([answer_text.casefold()])

        required_answers = set(self.get_required_answers())
        # verify all required answers are present
        if received_answers - received_answers:
            logging.info("Not all required answers present")
            logging.info(f"Required: {required_answers}")
            logging.info(f"Provided: {received_answers}")
            return False, list(received_answers - expected_answers)

        # validate there were no dulicate answers
        if len(received_answers) != len(user_answer.split(",")):
            logging.info("Duplicate answers")
            return False, list(received_answers - expected_answers)

        logging.info(f"Received answers: {received_answers}")
        logging.info(f"Correct answers: {expected_answers}")

        return received_answers.issubset(expected_answers), list(
            received_answers - expected_answers
        )


class AnswerGroup(BaseModel):
    """Group of answers."""

    group_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    header: Optional[str] = None
    answers: list[Answer]


class TestQuestion(BaseModel):
    """Card for testing japanese."""

    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parent_id: str
    header: str = ""
    question: str
    hint: str = ""
    answers: list[AnswerGroup]

    def to_json(self) -> dict:
        """Convert test card to JSON format.

        Returns
        -------
        dict
            Test card in JSON format.
        """
        return self.model_dump(mode="json")


def get_num_required_answers(answers: list[AnswerText]) -> int:
    """Provides number of required answers.

    Parameters
    ----------
    answers: list[AnswerText]
        List of answers to count required answers for.

    Returns
    -------
    int
        Number of required answers
    """
    return sum([1 for answer in answers if answer.required])
