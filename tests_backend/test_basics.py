"""Tests for basic Gaku functionality."""

import logging

import fsrs
import gaku
import gaku.api_types
import gaku.database
import gaku.card_types
from gaku.card_types import (
    KanjiCard,
    VocabCard,
    RadicalCard,
    CardType,
    create_card_from_json,
)
from gaku.api_types import StartTestRequest

from .utils import TestSetup, get_answer_for_question
from .test_data import VOCAB_CARD, KANJI_CARD, RADICAL_CARD


class TestBasics(TestSetup):
    """Tests for basic Gaku functionality."""

    def test_gaku_starts(self) -> None:
        """Validates that when Gaku starts, required files are created."""
        created_files = [f.name for f in self.tempdir.iterdir() if f.is_file()]

        logging.info("Checking generated files")
        assert "cards.db" in created_files

    def test_add_vocab_card(self) -> None:
        """Verifies that vocabulary card can be added to Gaku.."""
        logging.info("Adding Vocabulary card")
        self.manager.db.add_card(VOCAB_CARD)

        cards = self.manager.db.get_cards_any_state()
        logging.info(f"Got cards: {cards}")
        assert len(cards) == 1

        retrieved_card = cards[0]
        assert isinstance(retrieved_card, gaku.card_types.VocabCard)
        assert VOCAB_CARD.model_dump_json() == retrieved_card.model_dump_json()

    def test_add_kanji_card(self) -> None:
        """Verifies that Kanji card can be added to Gaku."""
        logging.info("Adding Kanji card")
        self.manager.db.add_card(KANJI_CARD)

        cards = self.manager.db.get_cards_any_state()
        logging.info(f"Got card: {cards}")
        assert len(cards) == 1

        retrieved_card = cards[0]
        assert isinstance(retrieved_card, gaku.card_types.KanjiCard)
        assert KANJI_CARD.model_dump_json() == retrieved_card.model_dump_json()

    def test_add_radical_card(self) -> None:
        """Verifies that Radical card can be added to Gaku."""
        logging.info("Adding Radical card")
        self.manager.db.add_card(RADICAL_CARD)

        cards = self.manager.db.get_cards_any_state()
        logging.info(f"Got cards: {cards}")
        assert len(cards) == 1

        retrieved_card = cards[0]
        assert isinstance(retrieved_card, gaku.card_types.RadicalCard)
        assert RADICAL_CARD.model_dump_json() == retrieved_card.model_dump_json()

    def test_generate_vocab_card_one(self) -> None:
        """Verifies that vocab card with one dictionary entry is
        generated correctly.
        """
        test_vocab = "隙あり"
        manager = self.manager

        generated_imports = manager.generate_vocab_import([test_vocab])
        logging.info(f"Generated cards for {test_vocab} are: {generated_imports}")
        vocab_cards = [
            card
            for card in generated_imports.generated_cards.values()
            if isinstance(card, VocabCard)
        ]
        logging.debug(f"Vocab cards: {vocab_cards}")
        assert len(vocab_cards) == 1
        card = vocab_cards[0]
        logging.info(f"Vocab card: {card}")
        assert card.card_type == CardType.VOCABULARY
        assert card.writing == test_vocab
        assert len(card.meanings) == 1
        meanings = card.meanings[0].meanings
        assert [meaning.answer_text for meaning in meanings] == [
            "chink in the armor (armour)"
        ]
        assert [reading.answer_text for reading in card.readings] == [
            "すきあり",
            "スキあり",
        ]

    def test_generate_kanji_card_both_readings(self) -> None:
        """Verifies Kanji cards are generated correctly when the kanji
        has both On and Kun readings.
        """
        test_kanji = "人"
        manager = self.manager

        generated_imports = manager.generate_kanji_import(test_kanji)
        logging.info(f"Generated cards for {test_kanji} are: {generated_imports}")

        kanji_cards = [
            card
            for card in generated_imports.generated_cards.values()
            if isinstance(card, KanjiCard)
        ]
        assert len(kanji_cards) == 1
        card = kanji_cards[0]
        assert card.card_type == CardType.KANJI
        assert card.writing == test_kanji
        assert [reading.answer_text for reading in card.on_readings] == ["ジン", "ニン"]
        assert [reading.answer_text for reading in card.kun_readings] == [
            "ひと",
            "-り",
            "-と",
        ]

    def test_generate_kanji_card_on_reading(self) -> None:
        """Verifies Kanji cards are generated correctly when the kanji
        has only On reading.
        """
        test_kanji = "格"
        manager = self.manager

        generated_imports = manager.generate_kanji_import(test_kanji)
        logging.info(f"Generated cards for {test_kanji} are: {generated_imports}")

        kanji_cards = [
            card
            for card in generated_imports.generated_cards.values()
            if isinstance(card, KanjiCard)
        ]
        assert len(kanji_cards) == 1
        card = kanji_cards[0]
        assert card.card_type == CardType.KANJI
        assert card.writing == test_kanji
        assert [reading.answer_text for reading in card.on_readings] == [
            "カク",
            "コウ",
            "キャク",
            "ゴウ",
        ]
        assert len(card.kun_readings) == 0

    def test_generate_kanji_card_kun_reading(self) -> None:
        """Verifies Kanji cards are generated correctly when the kanji
        has only Kun reading.
        """
        test_kanji = "椛"
        manager = self.manager

        generated_imports = manager.generate_kanji_import(test_kanji)
        logging.info(f"Generated cards for {test_kanji} are: {generated_imports}")

        kanji_cards = [
            card
            for card in generated_imports.generated_cards.values()
            if isinstance(card, KanjiCard)
        ]
        assert len(kanji_cards) == 1
        card = kanji_cards[0]
        assert card.card_type == CardType.KANJI
        assert card.writing == test_kanji
        assert len(card.on_readings) == 0
        assert [reading.answer_text for reading in card.kun_readings] == [
            "かば",
            "もみじ",
        ]

    def test_generate_radical_card(self) -> None:
        """Verifies that radical card can be imported."""
        test_radical = "人"
        manager = self.manager

        # TODO: the manager should be updated, so the generate radical
        #   doesn't require KanjiCard - so just use string
        #   or just add new API
        #   Possibly now using KanjiCard because of radical ID?
        generated_imports = manager.generate_kanji_import(test_radical)
        logging.info(f"Generated cards for {test_radical} are: {generated_imports}")
        radical_cards = [
            card
            for card in generated_imports.generated_cards.values()
            if isinstance(card, RadicalCard)
        ]
        assert len(radical_cards) == 1
        card = radical_cards[0]
        logging.info(f"Radical card is: {card}")
        assert card.card_type == CardType.RADICAL
        assert card.dictionary_id == 9
        assert card.writing == test_radical
        assert card.reading == "ひと"
        assert [meaning.answer_text for meaning in card.meanings] == ["person"]

    def test_import_and_test_new_cards(self) -> None:
        """Verifies that cards can be imported and test can be started
        using the start test session with new cards.
        """
        test_vocab = "隙あり"
        manager = self.manager

        generated_import = manager.generate_vocab_import([test_vocab])
        manager.import_cards(generated_import, sources=[])

        test_setup = StartTestRequest(num_cards=0, generate_extra_questions=False)
        manager.start_test_session_new_cards(test_setup)

        test = manager.test_session
        assert test is not None
        logging.info(f"Test started is: {test}")
        assert len(test.remaining_questions) == 5

        for num_responses in range(5):
            logging.info(f"Answering question {num_responses+1}")
            question = test.get_test_question()
            logging.info(f"Question is: {question}")
            question_data = question.next_question
            assert question_data is not None

            response = {
                answer.answer_id: ",".join([ans.answer_text for ans in answer.answers])
                for answer_group in question_data.answers
                for answer in answer_group.answers
            }

            # TODO: type the answer response
            answer_response = test.answer_question(response)
            logging.info(f"Answer response {answer_response}")

        finished_response = test.get_test_question()
        assert finished_response.next_question is None

    def test_import_and_test_any_state_cards(self) -> None:
        """Verifies that newly imported card can be tested
        using the start test session to test any state cards.
        """
        test_vocab = "隙あり"
        manager = self.manager

        generated_import = manager.generate_vocab_import([test_vocab])
        manager.import_cards(generated_import, sources=[])

        test_setup = StartTestRequest(num_cards=0, generate_extra_questions=False)
        manager.start_test_session(test_setup)

        test = manager.test_session
        assert test is not None
        logging.info(f"Test started is: {test}")
        assert len(test.remaining_questions) == 5

        for num_responses in range(5):
            logging.info(f"Answering question {num_responses+1}")
            question = test.get_test_question()
            logging.info(f"Question is: {question}")
            question_data = question.next_question
            assert question_data is not None

            response = {
                answer.answer_id: ",".join([ans.answer_text for ans in answer.answers])
                for answer_group in question_data.answers
                for answer in answer_group.answers
            }

            # TODO: type the answer response
            answer_response = test.answer_question(response)
            logging.info(f"Answer response {answer_response}")

        finished_response = test.get_test_question()
        assert finished_response.next_question is None

    def test_first_incorrect_answer_in_test_session(self) -> None:
        """Verifies that by default, after incorrect response,
        3 correct responses are needed.

        The responses are needed as follows:
        - 1 to verify user can answer correctly
        - 2 to help memorize the correct answer

        Validates that after one incorrect answer,
        3 correct answers are needed.
        """
        test_vocab = "隙あり"
        manager = self.manager

        generated_import = manager.generate_vocab_import([test_vocab])
        manager.import_cards(generated_import, sources=[])

        test_setup = StartTestRequest(
            num_cards=0, generate_extra_questions=False, card_types=[CardType.RADICAL]
        )
        manager.start_test_session(test_setup)

        test = manager.test_session
        assert test is not None
        logging.info(f"Test started is: {test}")
        assert len(test.remaining_questions) == 1

        logging.info("Sending incorrect answer.")
        question = test.get_test_question()
        # empty response should be treated as incorrect
        # TODO: verify multiple types of incorrect answers:
        # - incomplete
        # - correct, missing required answers - none or subset
        # - wrong answer id + correct answers - TODO: clarify behavior
        answer_response = test.answer_question({})
        assert answer_response is False

        for num_responses in range(3):
            logging.info(f"Answering question {num_responses+1}")
            question = test.get_test_question()
            logging.info(f"Question is: {question}")
            question_data = question.next_question
            assert question_data is not None

            response = {
                answer.answer_id: ",".join([ans.answer_text for ans in answer.answers])
                for answer_group in question_data.answers
                for answer in answer_group.answers
            }

            # TODO: type the answer response
            answer_response = test.answer_question(response)
            logging.info(f"Answer response {answer_response}")

        finished_response = test.get_test_question()
        assert finished_response.next_question is None
        assert test.is_session_finished()

    def test_first_multiple_incorrect_answers_in_test_session(self) -> None:
        """Verifies that by default, after incorrect response,
        3 correct responses are needed.

        The responses are needed as follows:
        - 1 to verify user can answer correctly
        - 2 to help memorize the correct answer

        Validates that after multiple incorrect answers,
        3 correct answers are still needed.
        """
        test_vocab = "隙あり"
        manager = self.manager

        generated_import = manager.generate_vocab_import([test_vocab])
        manager.import_cards(generated_import, sources=[])

        test_setup = StartTestRequest(
            num_cards=0, generate_extra_questions=False, card_types=[CardType.RADICAL]
        )
        manager.start_test_session(test_setup)

        test = manager.test_session
        assert test is not None
        logging.info(f"Test started is: {test}")
        assert len(test.remaining_questions) == 1

        NUM_INCORRECT_RESPONSES = 5
        for i in range(NUM_INCORRECT_RESPONSES):
            logging.info(f"Sending incorrect answer {i+1}/{NUM_INCORRECT_RESPONSES}.")
            question = test.get_test_question()
            # empty response should be treated as incorrect
            answer_response = test.answer_question({})
            assert answer_response is False

        for num_responses in range(3):
            logging.info(f"Answering question {num_responses+1}")
            question = test.get_test_question()
            assert question.next_question is not None
            logging.info(f"Question is: {question}")
            question_data = question.next_question

            response = {
                answer.answer_id: ",".join([ans.answer_text for ans in answer.answers])
                for answer_group in question_data.answers
                for answer in answer_group.answers
            }

            # TODO: type the answer response
            answer_response = test.answer_question(response)
            logging.info(f"Answer response {answer_response}")

        finished_response = test.get_test_question()
        assert finished_response.next_question is None
        assert test.is_session_finished()

    def test_edit_card(self) -> None:
        """Verifies data of card is correctly updated when updating it."""
        self.manager.db.add_card(VOCAB_CARD)

        edited_card = create_card_from_json(VOCAB_CARD.model_dump(mode="json"))
        assert isinstance(edited_card, VocabCard)
        edited_card.note = "note"

        self.manager.db.update_card(edited_card)

        cards = self.manager.db.get_cards_any_state()
        logging.info(f"Got cards: {cards}")
        assert len(cards) == 1

        retrieved_card = cards[0]
        assert retrieved_card.model_dump(mode="json") == edited_card.model_dump(
            mode="json"
        )

    def test_delete_card(self) -> None:
        """Verifies card can be deleted (without FSRS data)."""

        self.manager.db.add_card(VOCAB_CARD)

        cards = self.manager.db.get_cards_any_state()
        logging.info(f"Got cards: {cards}")
        assert len(cards) == 1

        logging.info("Deleting card")
        self.manager.db.delete_card(VOCAB_CARD.card_id)

        cards = self.manager.db.get_cards_any_state()
        logging.info(f"Got cards: {cards}")
        assert len(cards) == 0

    def test_fsrs_entry_created_after_incorrect_choice(self) -> None:
        """Verifies FSRS entry is created right after incorrect choice."""
        test_vocab = "隙あり"
        manager = self.manager

        generated_import = manager.generate_vocab_import([test_vocab])
        manager.import_cards(generated_import, sources=[])

        test_setup = StartTestRequest(
            num_cards=0, generate_extra_questions=False, card_types=[CardType.RADICAL]
        )
        manager.start_test_session(test_setup)

        test = manager.test_session
        assert test is not None
        logging.info(f"Test started is: {test}")
        assert len(test.remaining_questions) == 1

        question = test.get_test_question()
        assert question.test_card is not None
        card_id = question.test_card.card_id
        fsrs_card = manager.db.get_fsrs_data_for_card(card_id)
        assert fsrs_card is None

        logging.info("Sending incorrect answer.")
        test.answer_question({})
        test.get_test_question()

        fsrs_card = manager.db.get_fsrs_data_for_card(card_id)
        assert isinstance(fsrs_card, fsrs.Card)

    def test_fsrs_entry_created_after_correct_answer(self) -> None:
        """Verifies FSRS state after correctly answering all question for card."""

        test_vocab = "隙あり"
        manager = self.manager

        generated_import = manager.generate_vocab_import([test_vocab])
        manager.import_cards(generated_import, sources=[])

        test_setup = StartTestRequest(
            num_cards=0, generate_extra_questions=False, card_types=[CardType.RADICAL]
        )
        manager.start_test_session(test_setup)

        test = manager.test_session
        assert test is not None
        logging.info(f"Test started is: {test}")
        assert len(test.remaining_questions) == 1

        question = test.get_test_question()
        assert question.test_card is not None
        card_id = question.test_card.card_id

        while question.next_question is not None:
            test.answer_question(get_answer_for_question(question))
            question = test.get_test_question()

        assert test.is_session_finished()

        fsrs_card = manager.db.get_fsrs_data_for_card(card_id)
        assert fsrs_card is not None
        logging.info(f"FSRS data after completed test: {fsrs_card.to_dict()}")
        assert isinstance(fsrs_card, fsrs.Card)

    def test_create_edit_delete_source(self) -> None:
        """Verifies source can be created, updated and deleted."""

        manager = self.manager

        new_source = gaku.api_types.CardSource(
            source_name="source", source_section="section"
        )
        manager.db.add_card_source(new_source)

        all_sources = manager.db.get_card_sources_list()
        logging.info(f"Created sources: {all_sources}")
        assert len(all_sources) == 1
        db_source = all_sources[0]
        assert db_source.model_dump(mode="json") == new_source.model_dump(mode="json")

        updated_source = gaku.api_types.CardSource(**new_source.model_dump())
        updated_source.source_name = "updated source"
        updated_source.source_section = "updated section"
        manager.db.update_card_source(updated_source)

        updated_sources = manager.db.get_card_sources_list()
        logging.info(f"Updated sources are: {updated_sources}")
        assert len(updated_sources) == 1
        assert updated_sources[0].model_dump() == updated_source.model_dump()

        manager.db.delete_card_source(updated_source.source_id)

        deleted_sources = manager.db.get_card_sources_list()
        logging.info(f"Deleted sources list: {deleted_sources}")
        assert len(deleted_sources) == 0
