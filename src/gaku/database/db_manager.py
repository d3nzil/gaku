"""Database functionality for learning data."""

from datetime import datetime, timezone, timedelta

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from .db_schema import (
    TestCardsTable,
    FSRSTable,
    RecentMistakesTable,
)
from .db_sources import SourceManager
from .db_fsrs import FSRSManager
from .db_test_data import TestEntryManager
from .db_recent_mistakes import MistakesManager

from ..card_types import (
    TestCardTypes,
    MultiCard,
)
from ..api_types import CardFilter


class DbManager(SourceManager, FSRSManager, TestEntryManager, MistakesManager):
    """Database manager handles storing all learning data."""

    def get_fsrs_due_cards(
        self,
        filter: CardFilter,
    ) -> list[TestCardTypes]:
        """Get list of all cards with due date in the past.
        Oldest cards are first.
        """
        with Session(self.engine) as session:
            fsrs_select = (
                select(FSRSTable.card_id)
                .filter(FSRSTable.due_date <= datetime.now(timezone.utc))
                .order_by(FSRSTable.due_date)
            )
            if filter.num_cards is not None and filter.num_cards > 0:
                fsrs_select.limit(filter.num_cards)
            fsrs_ids = [card_id for card_id in session.scalars(fsrs_select)]

            card_select = select(TestCardsTable).filter(
                TestCardsTable.card_id.in_(fsrs_ids)
            )
            card_select = self.apply_card_filter_select(card_select, filter)
            return self.generate_cards_from_scalar(session.scalars(card_select))

    def get_num_fsrs_due_cards(self, filter: CardFilter) -> int:
        """Get number of all cards with due date in the past."""
        # disable the limits for counting
        filter.num_cards = None
        filter.start_index = None

        with Session(self.engine) as session:
            fsrs_select = select(FSRSTable.card_id).filter(
                FSRSTable.due_date <= datetime.now(timezone.utc)
            )
            fsrs_ids = [card_id for card_id in session.scalars(fsrs_select)]

            cards_select = select(TestCardsTable).filter(
                TestCardsTable.card_id.in_(fsrs_ids)
            )
            cards_select = self.apply_card_filter_select(cards_select, filter)

            num_cards = session.scalar(
                select(func.count()).select_from(cards_select.subquery())
            )
            if not isinstance(num_cards, int):
                raise RuntimeError("Could not count the new cards")

            return num_cards

    def get_studied_cards(self, filter: CardFilter) -> list[TestCardTypes]:
        """Gets already studied cards, but ignoring current due status.

        Parameters
        ----------
        filter: CardFilter
            Card filter to select cards.

        Returns
        -------
        list[TestCardTypes]
            Studied cards matching the filter
        """

        with Session(self.engine) as session:
            studied_select = self.apply_card_filter_select(
                select(TestCardsTable), filter
            ).filter(TestCardsTable.card_id.in_(session.query(FSRSTable.card_id)))

            return self.generate_cards_from_scalar(session.scalars(studied_select))

    def get_num_studied_cards(self, filter: CardFilter) -> int:
        """Gets number of studied cards matching the filter.

        Parameters
        ----------
        filter: CardFilter
            Card filter to select cards

        Returns
        -------
        int
            Number of studied cards matching the filter

        Raises
        ------
        RuntimeError
            If the cards could not be counted
        """

        # disable the limits for counting
        filter.num_cards = None
        filter.start_index = None

        with Session(self.engine) as session:
            studied_select = self.apply_card_filter_select(
                select(TestCardsTable.card_id), filter
            ).filter(TestCardsTable.card_id.in_(session.query(FSRSTable.card_id)))

            num_cards = session.scalar(
                select(func.count()).select_from(studied_select.subquery())
            )

            if not isinstance(num_cards, int):
                raise RuntimeError("Could not count studied cards")

            return num_cards

    def mistakes_get_num_mistakes_since(
        self, time_history: int, filter: CardFilter
    ) -> int:
        """Get number of all cards marked as mistakes in last num_days days."""
        with Session(self.engine) as session:
            timestamp = datetime.now() - timedelta(seconds=time_history)
            mistakes_select = select(RecentMistakesTable.card_id).filter(
                RecentMistakesTable.mistake_timestamp >= timestamp
            )
            card_ids = [card_id for card_id in session.scalars(mistakes_select)]

            cards_select = self.apply_card_filter_select(
                select(TestCardsTable).filter(TestCardsTable.card_id.in_(card_ids)),
                filter,
            )
            num_cards = session.scalar(
                select(func.count()).select_from(cards_select.subquery())
            )
            if not isinstance(num_cards, int):
                raise RuntimeError("Could not count the new cards")

            return num_cards

    def mistakes_get_mistakes_cards(
        self, time_history: int, filter: CardFilter
    ) -> list[TestCardTypes]:
        """Get list of all cards marked as mistakes in last num_days days."""
        with Session(self.engine) as session:
            timestamp = datetime.now() - timedelta(seconds=time_history)
            mistakes = select(RecentMistakesTable.card_id).filter(
                RecentMistakesTable.mistake_timestamp >= timestamp
            )
            card_ids = [card_id for card_id in session.scalars(mistakes)]

            cards_select = self.apply_card_filter_select(
                select(TestCardsTable).filter(TestCardsTable.card_id.in_(card_ids)),
                filter,
            )
            return self.generate_cards_from_scalar(session.scalars(cards_select))
