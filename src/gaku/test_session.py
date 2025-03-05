"""Test session related functionality."""

import logging
import random
from copy import deepcopy
from typing import Optional, Annotated, TypeVar

import fsrs
from pydantic import BaseModel, Field, field_serializer, field_validator, ConfigDict

from .card_types import TestQuestion, TestCardTypes, MultiCard
from .question import TestAnswer
from .database import DbManager
from .api_types import NextCardMessage, TestStatusMessage, CheckResult
from .config import get_config


T = TypeVar("T")

ExcludedField = Annotated[T, Field(exclude=True)]


class QuestionTestData(BaseModel):
    """Data for the question."""

    needs_correct_responses: int = get_config().required_answers
    mistakes: int = 0

    def mark_mistake(self) -> None:
        """Add mistake to the question."""
        self.needs_correct_responses = get_config().repeats_after_mistake + 1
        self.mistakes += 1
        logging.info(
            f"Adding mistake to the question, {self.mistakes} mistakes, {self.needs_correct_responses} remaining responses"
        )

    def mark_correct(self) -> None:
        """Add correct answer to the question."""
        self.needs_correct_responses -= 1
        logging.info(
            f"Adding correct answer to the question, {self.needs_correct_responses} remaining responses"
        )


class CardTestData(BaseModel):
    """Test data for a Card."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    card_id: str
    # FSRS data are for the parent card only, not the questions
    fsrs_data: fsrs.Card
    # generated questions are the question that were generated from the parent card
    # we need to keep track of them to know which cards to add back to the remaining cards
    question_test_data: dict[str, QuestionTestData]
    # for question in generated_cards:
    #     generated_questions[question.question_id] = QuestionTestData()

    num_mistakes: int = 0
    fsrs_marked: bool = False

    @field_serializer("fsrs_data")
    def serialize_fsrs_data(self, value: fsrs.Card) -> dict:
        """Converts FSRS Card to dict."""
        return value.to_dict()

    @field_validator("fsrs_data", mode="before")
    @classmethod
    def validate_fsrs_data(cls, value: dict) -> fsrs.Card:
        """Converts dict to FSRS Card if needed."""
        if isinstance(value, fsrs.Card):
            return value
        return fsrs.Card.from_dict(value)

    def mark_mistake(self, question_id: str) -> None:
        """Marks question as incorrectly answered.

        Parameters
        ----------
        question_id: str
            The id of question to mark.
        """
        logging.info(f"Marking mistake for {question_id}")
        self.question_test_data[question_id].mark_mistake()
        self.num_mistakes += 1

    def mark_correct(self, question_id: str) -> int:
        """Marks question as correctly answered.

        Parameters
        ----------
        question_id: str
            The id of the question to mark.
        """
        self.question_test_data[question_id].mark_correct()
        return self.question_test_data[question_id].needs_correct_responses

    def mark_entry(self, fsrs_manager: fsrs.Scheduler, db: DbManager) -> None:
        """Marks this card in FSRS database."""
        if self.num_mistakes and not self.fsrs_marked:
            # mark as mistake
            logging.info(f"FSRS - Marking card {self.card_id} as again")
            review, _ = fsrs_manager.review_card(
                self.fsrs_data, rating=fsrs.Rating.Again
            )
            db.update_card_fsrs(card_id=self.card_id, fsrs_card=review)
            db.mistakes_mark_mistake(card_id=self.card_id)
        else:
            # check if all generated cards are completed
            completed = all(
                card.needs_correct_responses == 0
                for card in self.question_test_data.values()
            )
            logging.info(f"{self.card_id} completed status: {completed}")
            if not completed:
                # do not mark the parent card if all generated cards are not completed
                return

            logging.info(f"FSRS - Marking card {self.card_id} as good")
            review, _ = fsrs_manager.review_card(
                self.fsrs_data, rating=fsrs.Rating.Good
            )
            db.update_card_fsrs(card_id=self.card_id, fsrs_card=review)

        self.fsrs_marked = True

    def is_completed(self) -> bool:
        """Checks if current test is finished.

        Returns
        -------
        bool
            True if test is finished, false otherwise.
        """
        return all(
            card.needs_correct_responses == 0
            for card in self.question_test_data.values()
        )


class TestSession(BaseModel):
    """Session for testing japanese."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    db: ExcludedField[DbManager]
    test_cards: dict[str, TestCardTypes] = {}
    remaining_questions: list[TestQuestion] = []
    current_question_set: list[TestQuestion] = []
    current_question: Optional[TestQuestion] = None
    question_card_data: dict[str, CardTestData] = {}
    fsrs_handler: ExcludedField[fsrs.Scheduler] = fsrs.Scheduler()
    mark_answers: bool = True
    num_current_cards: int = get_config().num_current_questions
    check_result: Optional[CheckResult] = None

    # statistics
    num_cards: int = 0
    num_correct_responses: int = 0
    num_incorrect_responses: int = 0
    num_completed_cards: int = 0
    num_questions: int = 0
    num_completed_questions: int = 0

    # configuration
    shuffle_questions: bool = True

    def load(self, card_data: list[TestCardTypes]) -> None:
        """Load cards from JSON data.

        Parameters
        ----------
        data : dict
            JSON data with cards.
        """
        _card_data = deepcopy(card_data)
        self.test_cards = {card.card_id: card for card in _card_data}
        for test_entry in self.test_cards.values():
            generated_questions = {
                question.question_id: question
                for question in test_entry.get_test_questions()
            }
            fsrs_data = (
                self.db.get_fsrs_data_for_card(test_entry.card_id) or fsrs.Card()
            )
            self.question_card_data[test_entry.card_id] = CardTestData(
                card_id=test_entry.card_id,
                fsrs_data=fsrs_data,
                question_test_data={
                    question.question_id: QuestionTestData()
                    for question in generated_questions.values()
                },
            )
            for test_question in generated_questions.values():
                self.remaining_questions.append(test_question)

        # set statistics
        self.num_cards = len(self.test_cards)
        self.num_correct_responses = 0
        self.num_incorrect_responses = 0
        self.num_completed_cards = 0
        self.num_questions = len(self.remaining_questions)
        self.num_completed_questions = 0

        # shuffle cards
        if self.shuffle_questions:
            random.shuffle(self.remaining_questions)
        logging.info(f"Loaded {len(self.test_cards)} cards")
        logging.debug(self.test_cards)
        logging.info(f"Remaining cards: {len(self.remaining_questions)}")

    def practice_failed_cards(self) -> None:
        """Practice only cards with mistakes."""

        # verify that test is finished
        if not self.is_session_finished():
            raise ValueError("Session is not finished")

        # get cards with mistakes
        cards_with_mistakes: list[TestCardTypes] = [
            card
            for card in self.test_cards.values()
            if self.question_card_data[card.card_id].num_mistakes > 0
        ]

        # load cards with mistakes
        self.load(cards_with_mistakes)

        # switch to practice mode
        self.mark_answers = False

    def practice_all_cards(self) -> None:
        """Practice all cards."""

        # verify that test is finished
        if not self.is_session_finished():
            raise ValueError("Session is not finished")

        # load all cards
        self.load(list(self.test_cards.values()))

        # switch to practice mode
        self.mark_answers = False

    def get_test_question(self) -> NextCardMessage:
        """Get next card to test.

        Returns
        -------
        NextCardMessage
            Object with the question data and card data or
            None if there are no more questions.
        """
        # check if current question was answered
        if self.check_result and self.check_result.question == self.current_question:
            if self.check_result.correct:
                self.mark_answer_correct(self.current_question.question_id)
            else:
                self.mark_answer_mistake(self.current_question.question_id)

        # if current card is not None, return it
        if self.current_question:
            logging.info(
                f"Current question is not None: {self.current_question.question_id}"
            )
            # test_card is parent card
            parent_card_id = self.current_question.parent_id
            parent_card = self.test_cards[parent_card_id]
            return NextCardMessage(
                next_question=self.current_question, test_card=parent_card
            )

        # if there are no remaining cards, return None
        if not self.remaining_questions and not self.current_question_set:
            logging.info("No more cards")
            return NextCardMessage()

        # if current card set is empty, fill it with defined amount of cards
        while (
            len(self.current_question_set) < self.num_current_cards
            and self.remaining_questions
        ):
            # take the first card to ensure the order is correct
            # for learning new cards (and to avoid getting the same card again)
            self.current_question_set.append(self.remaining_questions.pop(0))

        # get next card from the current card set
        self.current_question = self.current_question_set.pop(0)
        logging.info(f"Next card: {self.current_question.question_id}")
        parent_card_id = self.current_question.parent_id
        parent_card = self.test_cards[parent_card_id]
        return NextCardMessage(
            next_question=self.current_question, test_card=parent_card
        )

    def check_answer(self, answer_response: TestAnswer) -> bool:
        """Check if the answer is correct.

        Parameters
        ----------
        answer_response : dict
            Answer response.

        Returns
        -------
        bool
            True if the answer is correct, False otherwise.

        Raises
        ------
        ValueError
            If there is no current card.
        """

        if not self.current_question:
            raise ValueError("No current card")

        # check if the answer is correct
        answer_correct = all(
            [
                answer.check_answer(answer_response)
                for group in self.current_question.answers
                for answer in group.answers
            ]
        )
        self.check_result = CheckResult(
            question=self.current_question, correct=answer_correct
        )
        return answer_correct

    def mark_answer_correct(self, question_id: str) -> None:
        """Mark question as correct.

        Parameters
        ----------
        question_id : str
            Question ID.

        Raises
        ------
        ValueError
            If there is no current card.
        """
        if not self.current_question:
            raise ValueError("No current card")

        if not self.current_question.question_id == question_id:
            raise ValueError("Question ID does not match current card")

        logging.info(f"Marking question as correct: {question_id}")

        parent_card_id = self.current_question.parent_id
        current_question_parent = self.question_card_data[parent_card_id]

        # decrease number of correct responses needed
        remaining_responses = current_question_parent.mark_correct(question_id)
        logging.info(
            f"Correct answer for {question_id}, {remaining_responses} remaining"
        )

        # increase number of correct responses
        self.num_correct_responses += 1

        if remaining_responses >= 2:
            # >= means it was mistake before, so we want to show it sooner
            logging.info(f"Putting card to current cards: {question_id}")
            if self.shuffle_questions:
                random.shuffle(self.current_question_set)
            self.current_question_set.append(self.current_question)
        elif remaining_responses > 0:
            #  if the cards needs more correct responses, add it back to the remaining cards
            logging.info(f"Putting card back to remaining cards: {question_id}")
            if self.shuffle_questions:
                # shuffle the set
                random.shuffle(self.remaining_questions)
            # add card back to the remaining cards
            # this is done after shuffling to avoid
            # getting the same card again right away
            self.remaining_questions.append(self.current_question)
        else:
            logging.info(
                f"No more correct responses needed for {question_id}, remaining: {remaining_responses}"
            )
            self.num_completed_questions += 1

            # we reached the needed number of correct responses
            # so we can update the card
            # but only mark as good if the card has no mistakes
            if self.mark_answers:
                current_question_parent.mark_entry(self.fsrs_handler, self.db)

            # check if all parent cards are completed
            if current_question_parent.is_completed():
                self.num_completed_cards += 1

        # clear current card
        self.current_question = None
        self.check_result = None

    def mark_answer_mistake(self, question_id: str) -> None:
        """Mark question as incorrect.

        Parameters
        ----------
        question_id : str
            Question ID.

        Raises
        ------
        ValueError
            If there is no current card.
        """
        if not self.current_question:
            raise ValueError("No current card")

        if not self.current_question.question_id == question_id:
            raise ValueError("Question ID does not match current card")

        logging.info(f"Marking question as incorrect: {question_id}")

        parent_card_id = self.current_question.parent_id
        self.question_card_data[parent_card_id].mark_mistake(question_id)
        if self.mark_answers:
            self.question_card_data[parent_card_id].mark_entry(
                self.fsrs_handler, self.db
            )

        self.num_incorrect_responses += 1
        self.check_result = None

        # clear current card
        self.current_question

    def answer_question(self, answer_response: TestAnswer) -> bool:
        """Answer question.

        Parameters
        ----------
        answer : str
            Answer to the question.

        Returns
        -------
        bool
            True if answer is correct, False otherwise.
        """
        if not self.current_question:
            return False

        # check if the answer is correct
        answer_correct = self.check_answer(answer_response)

        if answer_correct:
            self.mark_answer_correct(self.current_question.question_id)
            return True

        # mark as mistake
        self.mark_answer_mistake(self.current_question.question_id)
        return False

    def get_test_results(self) -> dict:
        """Get test results of the session.

        Returns
        -------
        dict
            Test results.
        """
        stats: list[str] = []

        # get number of correct and incorrect cards
        num_cards = len(self.test_cards)
        num_cards_with_mistakes = len(
            [card for card in self.question_card_data.values() if card.num_mistakes > 0]
        )
        num_cards_correct = num_cards - num_cards_with_mistakes
        pct_cards_correct = (
            num_cards_correct / num_cards * 100 if len(self.test_cards) else 0
        )
        stats.append(
            f"Cards correct: {num_cards_correct}/{num_cards} ({pct_cards_correct:.2f}%)"
        )

        # get number of correct and incorrect questions
        question_stats = [
            question.mistakes
            for card in self.question_card_data.values()
            for question in card.question_test_data.values()
        ]
        num_questions = len(question_stats)
        num_questions_with_mistakes = len(
            [mistakes for mistakes in question_stats if mistakes > 0]
        )
        num_questions_correct = num_questions - num_questions_with_mistakes
        pct_questions_correct = (
            num_questions_correct / num_questions * 100 if num_questions else 0
        )
        stats.append(
            f"Questions correct: {num_questions_correct}/{num_questions} ({pct_questions_correct:.2f}%)"
        )

        return {
            "total_cards": self.num_cards,
            "correct_responses": self.num_correct_responses,
            "incorrect_responses": self.num_incorrect_responses,
            # TODO: get card with most mistakes or list of cards sorted by mistakes
            "stats": stats,
        }

    def get_session_status(self) -> TestStatusMessage:
        """Get number of completed and total cards in the session."""

        logging.info(f"All cards: {self.num_cards}")
        logging.info(f"Remaining cards: {len(self.remaining_questions)}")
        logging.info(f"Current card set: {len(self.current_question_set)}")

        return TestStatusMessage(
            cards_total=self.num_cards,
            cards_completed=self.num_completed_cards,
            questions_total=self.num_questions,
            questions_completed=self.num_completed_questions,
        )

    def wrap_up(self) -> None:
        """Wrap up the session - keep only cards with mistakes
        and current card set.
        """

        # keep only cards with mistakes
        self.test_cards = {
            card_id: card
            for card_id, card in self.test_cards.items()
            if self.question_card_data[card_id].num_mistakes > 0
        }

        # keep only current card set
        # TODO: this is broken, needs rework for current structure
        #   probably filter out questions with mistakes
        #   that still need to be answered
        self.current_question_set = [
            card
            for card in self.current_question_set
            if self.question_card_data[card.parent_id].num_mistakes > 0
        ]

        # clear current card set
        self.current_question_set = []

        # clear remaining cards
        self.remaining_questions = []

        # clear test data
        self.question_card_data = {}

    def is_session_finished(self) -> bool:
        """Check if the session is finished.

        Returns
        -------
        bool
            True if the session is finished, False otherwise.
        """
        return (
            not self.remaining_questions
            and not self.current_question_set
            and not self.current_question
        )
