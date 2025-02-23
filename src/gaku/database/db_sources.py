"""Database functionality for card sources."""

import json
from typing import List
from pathlib import Path

from sqlalchemy import (
    select,
)

from sqlalchemy.orm import (
    Session,
)

from .db_schema import DbManagerBase, CardSourceTable, CardSourceLinkTable
from .. import card_types


class SourceManager(DbManagerBase):
    """Manager for card sources database."""

    def __init__(self, connection_uri: str):
        super().__init__(connection_uri)

    # card source related methods
    def get_card_sources_list(self) -> List[card_types.CardSource]:
        """Get list of all card sources."""
        with Session(self.engine) as session:
            sources = session.query(CardSourceTable).all()
            return [
                card_types.CardSource(
                    source_id=source.source_id,
                    source_name=source.source_name,
                    source_section=source.source_section,
                )
                for source in sources
            ]

    def get_card_source_highest_position(self) -> int:
        """Returns current highest position in card source table.."""
        with Session(self.engine) as session:
            highest_position = (
                session.query(CardSourceTable.position)
                .order_by(CardSourceTable.position.desc())
                .first()
            )
            return highest_position[0] if highest_position is not None else 0

    def add_card_source(self, source: card_types.CardSource) -> None:
        """Adds card source to database."""
        highest_position = self.get_card_source_highest_position()
        with Session(self.engine) as session:
            session.add(
                CardSourceTable(
                    source_id=source.source_id,
                    position=highest_position + 1,
                    source_name=source.source_name,
                    source_section=source.source_section,
                )
            )
            session.commit()

    def update_card_source(self, source: card_types.CardSource) -> None:
        """Update card source in database."""
        with Session(self.engine) as session:
            source_db = (
                session.query(CardSourceTable)
                .filter(CardSourceTable.source_id == source.source_id)
                .first()
            )
            if source_db is None:
                raise ValueError(f"Card source with id {source.source_id} not found")
            source_db.source_name = source.source_name
            source_db.source_section = source.source_section
            session.commit()

    def delete_card_source(self, source_id: str) -> None:
        """Deletes source."""
        with Session(self.engine) as session:
            source_db = (
                session.query(CardSourceTable)
                .filter(CardSourceTable.source_id == source_id)
                .first()
            )
            if source_db is None:
                raise ValueError(f"Card source with id {source_id} not found")
            # TODO: handle deleting source references in link table
            session.delete(source_db)
            session.commit()

    def get_sources_for_card(self, card_id: str) -> List[card_types.CardSource]:
        """Gets sources attached to a card."""
        with Session(self.engine) as session:
            sources = (
                session.query(CardSourceTable)
                .join(CardSourceLinkTable)
                .filter(CardSourceLinkTable.card_id == card_id)
                .all()
            )
            return [card_types.CardSource(**source.to_dict()) for source in sources]

    def export_sources(self, export_path: Path) -> None:
        """Exports card sources into json file."""

        if export_path.exists():
            raise FileExistsError(
                "Export file already exists, cannot export. Please use different exkport path."
            )
        with open(export_path, "w", encoding="utf-8") as export_file:
            sources_get = select(CardSourceTable)
            with Session(self.engine) as session:
                db_sources: list[card_types.CardSource] = [
                    card_types.CardSource(
                        source_id=source.source_id,
                        source_name=source.source_name,
                        source_section=source.source_section,
                    )
                    for source in session.scalars(sources_get)
                ]

            export_file.write(
                json.dumps(
                    [source.model_dump(mode="json") for source in db_sources],
                    indent=2,
                    ensure_ascii=False,
                )
            )

    def import_sources(self, sources: list[card_types.CardSource]) -> None:
        """Imports card sources from json file into database, skipping existing sources."""

        with Session(self.engine) as session:
            existing_source_ids = {
                source.source_id for source in session.query(CardSourceTable).all()
            }
            new_sources = [
                CardSourceTable(
                    source_id=source.source_id,
                    source_name=source.source_name,
                    source_section=source.source_section,
                )
                for source in sources
                if source.source_id not in existing_source_ids
            ]
            session.add_all(new_sources)
            session.commit()

    def export_source_links(self, export_path: Path) -> None:
        """Exports card source links into json file."""

        if export_path.exists():
            raise FileExistsError(
                "Export file already exists, cannot export. Please use different exkport path."
            )
        with open(export_path, "w", encoding="utf-8") as export_file:
            sources_get = select(CardSourceLinkTable)
            with Session(self.engine) as session:
                db_sources_scalar = session.scalars(sources_get)
                if not isinstance(db_sources_scalar, list):
                    raise ValueError("Expected list of sources")
                db_sources: list[CardSourceLinkTable] = list(db_sources_scalar)

            export_file.write(
                json.dumps(
                    [source.to_dict() for source in db_sources],
                    indent=2,
                    ensure_ascii=False,
                )
            )

    def import_source_links(self, source_links: list[CardSourceLinkTable]) -> None:
        """Imports card source links from json file into database."""

        with Session(self.engine) as session:
            existing_links = {
                (link.card_id, link.source_id)
                for link in session.query(CardSourceLinkTable).all()
            }
            new_links = [
                CardSourceLinkTable(
                    card_id=source.card_id,
                    source_id=source.source_id,
                )
                for source in source_links
                if (source.card_id, source.source_id) not in existing_links
            ]
            session.add_all(new_links)
            session.commit()

    def get_card_source_link_ids(self, source_ids: List[str]) -> List[str]:
        """Retrieve card IDs linked to the given source IDs."""
        with Session(self.engine) as session:
            card_ids = (
                session.query(CardSourceLinkTable.card_id)
                .filter(CardSourceLinkTable.source_id.in_(source_ids))
                .all()
            )
            return [card_id for (card_id,) in card_ids]
