"""Functionality related to card scheduling."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import fsrs
from sqlalchemy import (
    select,
    func,
)
from sqlalchemy.orm import (
    Session,
)


from .db_schema import DbManagerBase, FSRSTable


class FSRSManager(DbManagerBase):
    """Manager for scheduling (FSRS) data."""

    def __init__(self, connection_uri: str) -> None:
        super().__init__(connection_uri)

    # FSRS related methods
    def get_fsrs_data_for_card(self, card_id: str) -> fsrs.Card | None:
        """Returns stored FSRS data for a card id."""
        logging.info(f"Getting FSRS data for card id: {card_id}")
        with Session(self.engine) as session:
            fsrs_card = (
                session.query(FSRSTable).filter(FSRSTable.card_id == card_id).first()
            )
            if fsrs_card is None:
                return None
                return fsrs.Card()
            logging.info(f"FSRS data found, returning: {fsrs_card.fsrs_data}")
            return fsrs.Card.from_dict(fsrs_card.fsrs_data)

    def update_card_fsrs(self, card_id: str, fsrs_card: fsrs.Card) -> None:
        """Updates FSRS card with new data, creates new if not exists."""

        logging.info(
            f"Updating FSRS for {card_id}, fsrs data: {fsrs_card}, new due date: {fsrs_card.due}"
        )
        with Session(self.engine) as session:
            fsrs_card_db = (
                session.query(FSRSTable).filter(FSRSTable.card_id == card_id).first()
            )
            if fsrs_card_db is None:
                logging.info("No FSRS entry yet, creating it")
                session.add(
                    FSRSTable(
                        card_id=card_id,
                        due_date=fsrs_card.due,
                        fsrs_data=fsrs_card.to_dict(),
                    )
                )
            else:
                fsrs_card_db.due_date = fsrs_card.due
                fsrs_card_db.fsrs_data = fsrs_card.to_dict()
            session.commit()

    def delete_card_fsrs(self, card_id: str) -> None:
        """Deletes FSRS data for a card id."""
        with Session(self.engine) as session:
            fsrs_card_db = (
                session.query(FSRSTable).filter(FSRSTable.card_id == card_id).first()
            )
            if fsrs_card_db is None:
                raise ValueError(f"FSRS card with id {card_id} not found")
            session.delete(fsrs_card_db)
            session.commit()

    def get_fsrs_num_due_cards(self) -> int:
        """Get number of all cards with due date in the past."""
        with Session(self.engine) as session:
            due_cards_count = (
                session.query(func.count(FSRSTable.card_id))
                .filter(FSRSTable.due_date <= datetime.now(timezone.utc))
                .scalar()
            )
        return due_cards_count

    def export_fsrs(self, export_path: Path) -> None:
        """Exports fsrs into json file."""

        if export_path.exists():
            raise FileExistsError(
                "Export file already exists, cannot export. Please use different exkport path."
            )
        with open(export_path, "w", encoding="utf-8") as export_file:
            fsrs_get = select(FSRSTable)
            with Session(self.engine) as session:
                db_fsrs: dict[str, dict] = {
                    fsrs_card.card_id: fsrs_card.fsrs_data
                    for fsrs_card in session.scalars(fsrs_get)
                }

            export_file.write(
                json.dumps(
                    db_fsrs,
                    indent=2,
                    ensure_ascii=False,
                )
            )

    def import_fsrs(self, fsrs_data: dict[str, fsrs.Card]) -> None:
        """Imports fsrs data from json file into database."""

        with Session(self.engine) as session:
            fsrs_db = [
                FSRSTable(
                    card_id=fsrs_id,
                    due_date=fsrs_card.due,
                    fsrs_data=fsrs_card.to_dict(),
                )
                for fsrs_id, fsrs_card in fsrs_data.items()
            ]
            session.add_all(fsrs_db)

            session

    def get_num_due_by_date(self, date: datetime) -> int:
        """Gets number of all cards with due date in the past."""
        with Session(self.engine) as session:
            due_cards_count = (
                session.query(func.count(FSRSTable.card_id))
                .filter(FSRSTable.due_date <= date)
                .scalar()
            )
        return due_cards_count
