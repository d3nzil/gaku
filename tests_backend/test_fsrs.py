"""Verifies FSRS related functionality."""

from datetime import timedelta
import logging

import fsrs
import gaku
import gaku.api_types
import gaku.database
import gaku.card_types

from .utils import TestSetup
from .test_data import VOCAB_CARD, KANJI_CARD


class TestFsrs(TestSetup):
    """Verifies FSRS (card scheduling) related functionality."""

    def test_fsrs_due_in_correct_order(self) -> None:
        """Verify that when getting due cards, they are returned
        from oldest due date to most recent.
        """

        logging.info("Creating cards and adding FSRS recors")
        self.manager.db.add_cards([VOCAB_CARD, KANJI_CARD])

        vocab_fsrs = fsrs.Card()
        vocab_fsrs.due = vocab_fsrs.due - timedelta(hours=1)
        kanji_fsrs = fsrs.Card()
        kanji_fsrs.due = kanji_fsrs.due - timedelta(days=1)

        self.manager.db.update_card_fsrs(VOCAB_CARD.card_id, vocab_fsrs)
        self.manager.db.update_card_fsrs(KANJI_CARD.card_id, kanji_fsrs)

        logging.info("Verifiying that oldest card is provided first")
        card_filter = gaku.api_types.CardFilter(num_cards=1)

        # multiple tries, since I was getting random errors for unknown reason
        # vanished when I added fixed card_id to all the test cards, but might
        # still be in there
        for i in range(100):
            logging.info("Check number: {i+1}/100")
            due_cards = self.manager.db.get_fsrs_due_cards(filter=card_filter)
            assert len(due_cards) == 1
            assert due_cards[0].card_id == KANJI_CARD.card_id
