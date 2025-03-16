"""Various data structures."""

from typing import Optional

from pydantic import BaseModel, Field

from . import card_types
from .card_types import (
    TestCardTypes,
    CardSource,
    CardType,
    TestQuestion,
    MultiCard,
    VocabCard,
    KanjiCard,
    RadicalCard,
)


class AnswerResponseMessage(BaseModel):
    """Response message for the answer."""

    correct_answer: bool
    next_question: Optional[TestQuestion] = None
    test_card: Optional[TestCardTypes] = None


class NextCardMessage(BaseModel):
    """Message with the next card.

    Attributes
    ----------
    test_card : Optional[TestCardTypes]
        Test card, None if there are no more cards.
    next_question : Optional[TestQuestion]
        The question to display, None if there are no more questions.
    """

    test_card: Optional[TestCardTypes] = None
    next_question: Optional[TestQuestion] = None


class TestResultsMessage(BaseModel):
    """Message with the test results.

    Attributes
    ----------
    correct : int
        Number of correct answers.
    total : int
        Total number of questions.
    """

    correct: int
    total: int


class CardFilter(BaseModel):
    """Message with the card filter.

    Attributes
    ----------
    card_sources : Optional[list[CardSource]]
        List of card sources.
    card_types : Optional[list[CardType]]
        List of card types.
    search_text : str
        Text to find in card data.
    num_cards : Optional[int]
        Number of cards.
    start_index : Optional[int]
        Index of the first card.
    """

    card_sources: list[CardSource] = []
    card_types: list[CardType] = []
    search_text: str = ""
    num_cards: Optional[int] = None
    start_index: Optional[int] = None


class StartTestRequest(CardFilter):
    """Message with the test start request.
    Extends CardFilter.

    Attributes
    ----------
    mark_answers : bool
        If True, the answers will be marked.
    """

    mark_answers: bool = True
    generate_extra_questions: bool = True


class TestStatusMessage(BaseModel):
    """Message with the test status."""

    questions_completed: int
    questions_total: int
    cards_completed: int
    cards_total: int


class ImportItem(BaseModel):
    """Item to import."""

    item_id: str
    sub_items: list["ImportItem"] = Field(default_factory=list)


class GeneratedImports(BaseModel):
    """Message with the cards generated from import data."""

    # list of generated items ids in order
    import_items: list[ImportItem] = Field(default_factory=list)
    # generated test cards - key is the card id
    generated_cards: dict[
        str, VocabCard | KanjiCard | RadicalCard | card_types.OnomatopoeiaCard
    ] = Field(default_factory=dict)
    # list of ids of new cards (not yet in the database)
    new_card_ids: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class ImportRequest(BaseModel):
    """Import request message representation."""

    cards: GeneratedImports
    sources: list[CardSource]


class CheckResult(BaseModel):
    """Result of the answer check."""

    question: TestQuestion
    correct: bool


class CardSourceLink(BaseModel):
    """Representation of card source link."""

    position: int = -1
    card_id: str
    source_id: str


class AnswerCheckResponse(BaseModel):
    """Result of answer correctness check."""

    all_correct: bool
    mistakes: dict[str, list[str]]
