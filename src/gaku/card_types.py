"""Card related functionality."""

import logging
import random
import uuid
from enum import Enum
from typing import Optional, Union
from pydantic import BaseModel, Field


from .config import get_config
from .question import AnswerType, AnswerText, Answer, AnswerGroup, TestQuestion


class CardSource(BaseModel):
    """Source of the card.

    Typically, this is a book or a website.
    The source_section is used to specify the section of the source (chapter, lesson, url...).
    """

    source_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_name: str = Field(min_length=1)
    source_section: Optional[str] = None


class CardType(Enum):
    """Type of the entry."""

    KANJI = "KANJI"
    VOCABULARY = "VOCABULARY"
    RADICAL = "RADICAL"
    QUESTION = "QUESTION"
    ONOMATOPOEIA = "ONOMATOPOEIA"
    MULTI_CARD = "MULTI_CARD"


class BaseCard(BaseModel):
    """Base class for all cards."""

    card_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # dictionary unique identifier as there can be multiple entries for the same word in dictionary
    dictionary_id: Optional[int] = None
    custom_questions: list[TestQuestion] = []
    note: str = ""
    hint: str = ""


class VocabularyMeaningEntry(BaseModel):
    """Vocabulary meaning entry."""

    # meaning: VocabularyMeaning
    test_enabled: bool = True
    part_of_speech: str
    meanings: list[AnswerText]


class VocabCard(BaseCard):
    """Entry for Japanese vocabulary."""

    card_type: CardType = CardType.VOCABULARY

    writing: str
    reading_type: AnswerType = AnswerType.HIRAGANA
    readings: list[AnswerText]
    meanings: list[VocabularyMeaningEntry]
    # TODO:
    # - add support for kanji and kanji test cards for vocabulary entries

    def get_meanings_test_question(self) -> TestQuestion:
        """Get test question for meanings.

        Returns
        -------
        TestQuestion
            Test question for meanings.

        Raises
        ------
        ValueError
            If there are no meanings to test.
        """
        meanings_answers = []
        for idx, meaning_entry in enumerate(self.meanings):
            if not meaning_entry.test_enabled:
                continue

            if meaning_entry.part_of_speech != "":
                header = f"{idx+1}. Vocab meanings\n({meaning_entry.part_of_speech})"
            else:
                header = f"{idx+1}. Vocab meanings\n"

            meanings_answers.append(
                Answer(
                    answer_type=AnswerType.ROMAJI,
                    header=header,
                    hint=self.hint or "",
                    answers=meaning_entry.meanings,
                )
            )

        if not meanings_answers:
            raise ValueError(f"No meanings to test for: {self}")

        return TestQuestion(
            parent_id=self.card_id,
            header="Vocab meaning",
            question=self.writing,
            hint=self.hint
            or ", ".join([reading.answer_text for reading in self.readings]),
            answers=[AnswerGroup(answers=meanings_answers)],
        )

    def get_readings_test_question(self) -> TestQuestion:
        """Get test question for readings.

        Returns
        -------
        TestQuestion
            Test question for readings.

        Raises
        ------
        ValueError
            If there are no readings to test.
        """
        if not self.readings:
            raise ValueError("No readings to test")

        return TestQuestion(
            parent_id=self.card_id,
            header="Vocab reading",
            question=self.writing,
            hint=self.hint
            or ", ".join(
                [meaning.answer_text for meaning in self.meanings[0].meanings]
            ),
            answers=[
                AnswerGroup(
                    answers=[
                        Answer(
                            answer_type=self.reading_type,
                            header="Vocab readings",
                            answers=self.readings,
                        )
                    ]
                )
            ],
        )

    def get_test_questions(self) -> list[TestQuestion]:
        """Get test cards for the vocabulary entry.

        Returns
        -------
        list[TestCard]
            List of test cards.
            Typically following cards are created:
            - Q: writing, A: readings
            - Q: writing, A: meanings
        """
        cards = []
        cards.append(self.get_meanings_test_question())
        if self.readings:
            cards.append(self.get_readings_test_question())

        return cards + self.custom_questions


class KanjiCard(BaseCard):
    """Entry for Japanese kanji."""

    # TODO:
    # - add support for radical and radical test cards for kanji entries
    card_type: CardType = CardType.KANJI

    writing: str
    on_readings: list[AnswerText]
    kun_readings: list[AnswerText]
    meanings: list[AnswerText]
    radical_id: Optional[int]

    def get_meanings_test_question(self) -> TestQuestion:
        """Get test question for meanings.

        Returns
        -------
        TestQuestion
            Test question for meanings.
        """
        return TestQuestion(
            parent_id=self.card_id,
            header="Kanji meaning",
            question=self.writing,
            answers=[
                AnswerGroup(
                    answers=[
                        Answer(
                            answer_type=AnswerType.ROMAJI,
                            header="Kanji meanings",
                            answers=self.meanings,
                        )
                    ],
                )
            ],
        )

    def get_readings_test_question(self) -> TestQuestion:
        """Get test question for readings.

        Returns
        -------
        TestQuestion
            Test question for readings.
        """
        kanji_readings_answers = []
        if self.on_readings:
            kanji_readings_answers.append(
                Answer(
                    answer_type=AnswerType.KATAKANA,
                    header="On Readings",
                    answers=self.on_readings,
                )
            )
        if self.kun_readings:
            # kun readings include okurigana, so we strip them
            kun_readings = [
                reading.answer_text.split(".")[0] for reading in self.kun_readings
            ]
            # and drop duplicates, while keeping the order
            kun_readings = list(dict.fromkeys(kun_readings))

            kanji_readings_answers.append(
                Answer(
                    answer_type=AnswerType.HIRAGANA,
                    header="Kun Readings",
                    answers=[
                        AnswerText(answer_text=reading) for reading in kun_readings
                    ],
                )
            )

        return TestQuestion(
            parent_id=self.card_id,
            header="Kanji readings",
            question=self.writing,
            hint=", ".join([meaning.answer_text for meaning in self.meanings]),
            answers=[AnswerGroup(answers=kanji_readings_answers)],
        )

    def get_test_questions(self) -> list[TestQuestion]:
        """Get test cards for the kanji entry.

        Returns
        -------
        list[TestCard]
            List of test cards.
            Typically following cards are created:
            - Q: character, A: on readings
            - Q: character, A: kun readings
            - Q: character, A: meanings
        """
        cards = []
        cards.append(self.get_meanings_test_question())
        cards.append(self.get_readings_test_question())

        return cards + self.custom_questions


class RadicalCard(BaseCard):
    """Entry for Japanese radical."""

    card_type: CardType = CardType.RADICAL

    writing: str
    meanings: list[AnswerText]
    reading: str

    def get_test_questions(self) -> list[TestQuestion]:
        """Get test cards for the radical entry.

        Returns
        -------
        list[TestCard]
            List of test cards.
            Typically following cards are created:
            - Q: character, A: meanings
        """
        test_questions = []
        if get_config().radicals_test_meaning:
            test_questions.append(
                Answer(
                    answer_type=AnswerType.ROMAJI,
                    header="Radical meanings",
                    answers=self.meanings,
                )
            )
        test_questions.append(
            Answer(
                answer_type=AnswerType.HIRAGANA,
                header="Radical reading",
                answers=[AnswerText(answer_text=self.reading)],
            )
        )

        # create a card for the radical
        test_cards = []
        test_cards.append(
            TestQuestion(
                parent_id=self.card_id,
                header="Radical",
                question=self.writing,
                answers=[AnswerGroup(answers=test_questions)],
            )
        )

        return test_cards + self.custom_questions


class OnomatopoeiaDefinition(BaseModel):
    """Onomatopoeia definition."""

    equivalent: list[AnswerText]
    meaning: AnswerText


class OnomatopoeiaCard(BaseCard):
    """Onomatopoeia entry."""

    card_type: CardType = CardType.ONOMATOPOEIA

    # copy of j-ono structure
    # hiragana: list[str]
    # katakana: list[str]
    # definition: list[dict]
    #   equivalent: list[str]
    #   meaning: str
    #   example - probably ignore
    # literal: str
    #   -> writing
    writing: str
    kana_writing: list[str]
    definitions: list[OnomatopoeiaDefinition]

    def get_test_questions(self) -> list[TestQuestion]:
        """Creates test question for this Onomatopoeia card."""

        return [
            TestQuestion(
                parent_id=self.card_id,
                header="Onomatopoeia meaning",
                question=", ".join(self.kana_writing),
                answers=[
                    AnswerGroup(
                        answers=[
                            Answer(
                                answer_type=AnswerType.ROMAJI,
                                header=f"{i+1}. meaning",
                                answers=definition.equivalent,
                            )
                            for i, definition in enumerate(self.definitions)
                        ]
                    )
                ],
            )
        ]


class QuestionCard(BaseCard):
    """Card for custom questions."""

    card_type: CardType = CardType.QUESTION

    # question to ask (question would be better, but for api consistency we use writing)
    writing: str
    answers: list[Answer]

    def get_test_questions(self) -> list[TestQuestion]:
        """Creates test questions for this card."""
        return [
            TestQuestion(
                parent_id=self.card_id,
                header="Custom question",
                question=self.writing,
                answers=[AnswerGroup(answers=self.answers)],
            )
        ] + self.custom_questions


class MultiCard(BaseCard):
    """Card for testing sets of cards.

    This card is used to group multiple cards together.
    """

    writing: str = ""

    card_type: CardType = CardType.MULTI_CARD
    multicard_type: CardType
    # card ids are needed to get the cards from the database
    # this is needed because the cards can be changed there
    # and we always want to use the most recent version
    card_ids: list[str]
    cards: list[VocabCard | KanjiCard | RadicalCard]
    # options - only for vocab and kanji cards
    # for radicals we always test both meanings and readings
    test_readings: bool = True
    test_meanings: bool = True

    def update_writing(self) -> None:
        """Generate writing from the card ids."""
        self.writing = " - ".join([card.writing for card in self.cards])

    def get_test_questions(self) -> list[TestQuestion]:
        """Get test cards for the multi card.

        Returns
        -------
        list[TestCard]
            List of test cards.
        """
        logging.info(f"Creating test questions for multi card: {self}")
        logging.info(f"Card ids: {self.card_ids}")

        self.update_writing()

        questions = []

        if self.multicard_type == CardType.RADICAL:
            logging.info(f"Creating radical test question for multi card: {self}")
            radical_questions = []

            # convert the questions to multi card questions
            radical_multi_question = TestQuestion(
                parent_id=self.card_id,
                header="Radical",
                question=self.writing,
                answers=[],
            )
            for card in self.cards:
                radical_questions = card.get_test_questions()
                if len(radical_questions) > 1:
                    raise ValueError(
                        f"Radical card with multiple questions: {radical_questions}"
                    )
                question = radical_questions[0]
                if len(question.answers) > 1:
                    raise ValueError(
                        f"Radical question with multiple answers: {radical_questions}"
                    )
                answer_group = question.answers[0]
                answer_group.header = card.writing
                radical_multi_question.answers.append(answer_group)

            # shuffle the order of the questions
            random.shuffle(radical_multi_question.answers)
            questions.append(radical_multi_question)

        elif self.multicard_type in [CardType.VOCABULARY, CardType.KANJI]:

            if self.test_meanings:
                logging.info(f"Creating meanings test question for multi card: {self}")
                question = TestQuestion(
                    parent_id=self.card_id,
                    header="Meanings",
                    question=self.writing,
                    answers=[],
                )
                for card in self.cards:
                    if not isinstance(card, (VocabCard, KanjiCard)):
                        raise ValueError(
                            f"Multi card with card type {card.card_type} not supported"
                        )
                    card_question = card.get_meanings_test_question()
                    if len(card_question.answers) > 1:
                        raise ValueError(
                            f"Vocab question with multiple answers: {card_question}"
                        )
                    answer_group = card_question.answers[0]
                    answer_group.header = card.writing
                    question.answers.append(answer_group)

                # shuffle the order of the questions
                random.shuffle(question.answers)
                logging.info(f"Meanings test question for multi card: {question}")
                questions.append(question)
            else:
                logging.info("Skipping meanings test question for multi card")

            if self.test_readings:
                logging.info(f"Creating readings test question for multi card: {self}")
                question = TestQuestion(
                    parent_id=self.card_id,
                    header="Readings",
                    question=self.writing,
                    answers=[],
                )
                for card in self.cards:
                    if not isinstance(card, (VocabCard, KanjiCard)):
                        raise ValueError(
                            f"Multi card with card type {card.card_type} not supported"
                        )
                    card_question = card.get_readings_test_question()
                    if len(card_question.answers) > 1:
                        raise ValueError(
                            f"Vocab question with multiple answers: {card_question}"
                        )

                    answer_group = card_question.answers[0]
                    answer_group.header = card.writing
                    question.answers.append(answer_group)

                # shuffle the order of the questions
                random.shuffle(question.answers)
                logging.info(f"Readings test question for multi card: {question}")
                questions.append(question)
            else:
                logging.info("Skipping readings test question for multi card")

        else:
            raise ValueError(f"Multi card type {self.multicard_type} not supported")

        if len(questions) == 0:
            raise ValueError(f"No questions for multi card: {self}")
        return questions


TestCardTypes = Union[
    VocabCard, KanjiCard, RadicalCard, QuestionCard, MultiCard, OnomatopoeiaCard
]


def create_card_from_json(card_data: dict) -> TestCardTypes:
    """Creates a card from json data."""
    card_type = CardType(card_data["card_type"])
    if card_data["card_id"] == "":
        card_data["card_id"] = str(uuid.uuid4())

    if card_type == CardType.VOCABULARY:
        return VocabCard(**card_data)
    elif card_type == CardType.KANJI:
        return KanjiCard(**card_data)
    elif card_type == CardType.RADICAL:
        return RadicalCard(**card_data)
    elif card_type == CardType.QUESTION:
        return QuestionCard(**card_data)
    elif card_type == CardType.MULTI_CARD:
        logging.info(f"Creating multi card from json: {card_data}")
        cards = [create_card_from_json(card) for card in card_data["cards"]]
        card_data["cards"] = cards
        return MultiCard(**card_data)
    elif card_type == CardType.ONOMATOPOEIA:
        logging.info(f"Creating Onomatopoeia card")
        return OnomatopoeiaCard(**card_data)
    else:
        raise ValueError(f"Card type {card_type} not supported")
