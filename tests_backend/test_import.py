"""Gaku tests focusing on generating imports and importing cards."""

import logging

import gaku
import gaku.api_types
import gaku.database
import gaku.card_types

from .utils import TestSetup


class TestImport(TestSetup):
    """Verifies import related Gaku fucntionality."""

    def test_import_cards_without_source(self) -> None:
        """Verifies cards without source can be imported."""
        test_vocab = "隙あり"
        manager = self.manager

        generated_import = manager.generate_vocab_import([test_vocab])
        manager.import_cards(generated_import, sources=[])

        cards = manager.db.get_cards_any_state()
        logging.info(f"Cards got after import: {cards}")
        assert len(cards) == 3

    def test_import_cards_with_source(self) -> None:
        """Verifies cards with source can be imported."""
        test_vocab = "隙あり"
        manager = self.manager

        source = gaku.api_types.CardSource(
            source_name="source", source_section="section"
        )
        manager.db.add_card_source(source)

        generated_import = manager.generate_vocab_import([test_vocab])
        manager.import_cards(generated_import, sources=[source])

        cards = manager.db.get_cards_any_state()
        logging.info(f"Cards got after import with source: {cards}")
        assert len(cards) == 3

        source_search = gaku.api_types.CardFilter(card_sources=[source])
        cards = manager.db.get_cards_any_state(filter=source_search)
        assert len(cards) == 3

    def test_reimport_cards_without_source(self) -> None:
        """Verifies re-importing same cards again doesn't result in
        duplicate card entries.
        """
        test_vocab = "隙あり"
        manager = self.manager

        generated_import = manager.generate_vocab_import([test_vocab])
        manager.import_cards(generated_import, sources=[])

        cards = manager.db.get_cards_any_state()
        logging.info(f"Cards got after import: {cards}")
        assert len(cards) == 3

        manager.import_cards(generated_import, sources=[])

        cards = manager.db.get_cards_any_state()
        logging.info(f"Cards got after re-import of the same cards: {cards}")
        assert len(cards) == 3

    def test_reimport_cards_add_source(self) -> None:
        """Verifies source can be added when re-importing
        the same cards again, but with source.
        """

        test_vocab = "隙あり"
        manager = self.manager

        source = gaku.api_types.CardSource(
            source_name="source", source_section="section"
        )
        manager.db.add_card_source(source)

        generated_import = manager.generate_vocab_import([test_vocab])
        manager.import_cards(generated_import, sources=[])

        cards = manager.db.get_cards_any_state()
        assert len(cards) == 3

        source_search = gaku.api_types.CardFilter(card_sources=[source])
        cards = manager.db.get_cards_any_state(filter=source_search)
        logging.info(f"Cards got after import: {cards}")
        assert len(cards) == 0

        logging.info("Re-importing the cards with source")
        manager.import_cards(generated_import, sources=[source])

        cards = manager.db.get_cards_any_state()
        logging.info(f"Cards got after re-import, search without filter: {cards}")
        assert len(cards) == 3

        source_search = gaku.api_types.CardFilter(card_sources=[source])
        logging.info(f"Cards got after re-import, search with source filter: {cards}")
        cards = manager.db.get_cards_any_state(filter=source_search)
        assert len(cards) == 3

    def test_import_of_得る(self) -> None:
        """Verifies that 得る is imported correctly.

        Based on a problem of having two meanings together.
        Turned out the meanings were together in the dictionary,
        but keeping this as importing needs to be verified anyway.
        """
        test_vocab = "得る"
        manager = self.manager

        source = gaku.api_types.CardSource(
            source_name="source", source_section="section"
        )
        manager.db.add_card_source(source)

        generated_import = manager.generate_vocab_import([test_vocab])

        generated_cards = [
            card
            for card in generated_import.generated_cards.values()
            if isinstance(card, gaku.card_types.VocabCard)
            and card.dictionary_id == 1588760
        ]
        assert len(generated_cards) == 1
        card = generated_cards[0]
        meanings: list[str] = [
            meaning.answer_text
            for meaning_group in card.meanings
            for meaning in meaning_group.meanings
        ]
        logging.info(f"Generated card meanings: {meanings}")
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
