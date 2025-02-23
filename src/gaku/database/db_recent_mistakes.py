"""Functionality related for recent mistakes."""

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from .db_schema import RecentMistakesTable, DbManagerBase


class MistakesManager(DbManagerBase):
    """Manager for recent mistakes."""

    def __init__(self, connection_uri: str) -> None:
        super().__init__(connection_uri)

    def mistakes_cleanup(self) -> None:
        """Removes all mistakes older than 7 days."""
        with Session(self.engine) as session:
            session.query(RecentMistakesTable).filter(
                RecentMistakesTable.mistake_timestamp
                < (datetime.now() - timedelta(days=7))
            ).delete()
            session.commit()

    def mistakes_mark_mistake(self, card_id: str) -> None:
        """Marks card as mistake."""
        with Session(self.engine) as session:
            # check if card is already in mistakes
            existing_mistake = (
                session.query(RecentMistakesTable)
                .filter(RecentMistakesTable.card_id == card_id)
                .first()
            )
            if existing_mistake is not None:
                existing_mistake.mistake_timestamp = datetime.now()
            else:
                session.add(
                    RecentMistakesTable(
                        card_id=card_id, mistake_timestamp=datetime.now()
                    )
                )
            session.commit()

    def mistakes_get_num_mistakes_by_day(self) -> dict:
        """Returns number of mistakes per day."""
        mistakes_by_day = {}

        with Session(self.engine) as session:
            for i in range(7):
                day = datetime.now() - timedelta(days=i + 1)
                mistakes = (
                    session.query(RecentMistakesTable)
                    .filter(
                        RecentMistakesTable.mistake_timestamp >= day,
                        RecentMistakesTable.mistake_timestamp < day + timedelta(days=1),
                    )
                    .count()
                )
                mistakes_by_day[i + 1] = mistakes

        return mistakes_by_day
