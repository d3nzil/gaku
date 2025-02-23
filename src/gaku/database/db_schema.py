"""Database schema and base functionality."""

from enum import Enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    ForeignKey,
    String,
    JSON,
    create_engine,
    DateTime,
    Integer,
    Index,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)


class TableNames(Enum):
    """Mapping of table names."""

    CARD_SOURCE = "card_source"
    CARD_SOURCE_LINK = "card_source_link"
    TEST_CARDS = "test_cards"
    FSRS = "fsrs"


class Base(DeclarativeBase):
    """Base tabale for Gaku."""

    pass


class CardSourceTable(Base):
    """Source of the card.

    Typically, this is a book or a website.
    The source_section is used to specify the section of the source (chapter, lesson, url...).
    """

    __tablename__ = TableNames.CARD_SOURCE.value

    source_id: Mapped[str] = mapped_column(
        String(length=36), primary_key=True, index=True
    )
    position: Mapped[int] = mapped_column(Integer)

    source_name: Mapped[str] = mapped_column(String())
    # TODO: should the section be separate table?
    source_section: Mapped[Optional[str]]

    def to_dict(self) -> dict:
        """Export sources as dict."""
        return {
            "source_id": self.source_id,
            "source_name": self.source_name,
            "source_section": self.source_section,
        }


class CardSourceLinkTable(Base):
    """Link table between card and source.

    This table is needed, because card can have multiple sources and we want to keep track of them.
    """

    __tablename__ = TableNames.CARD_SOURCE_LINK.value

    position: Mapped[int] = mapped_column(unique=False, nullable=False)
    card_id: Mapped[str] = mapped_column(
        ForeignKey(f"{TableNames.TEST_CARDS.value}.card_id"), primary_key=True
    )
    source_id: Mapped[str] = mapped_column(
        ForeignKey(f"{TableNames.CARD_SOURCE.value}.source_id"), primary_key=True
    )

    __table_args__ = (Index("idx_position_source", "position", "source_id"),)

    def to_dict(self) -> dict:
        """Exports source links as dict."""
        return {
            "card_id": self.card_id,
            "position": self.position,
            "source_id": self.source_id,
        }


class TestCardsTable(Base):
    """Table for card data."""

    __tablename__ = TableNames.TEST_CARDS.value

    card_id: Mapped[str] = mapped_column(
        String(length=36), primary_key=True, index=True
    )
    dictionary_id: Mapped[Optional[int]]
    position: Mapped[int] = mapped_column(Integer, index=True)

    card_type: Mapped[str] = mapped_column(String(), index=True)

    key: Mapped[str] = mapped_column(String(), index=True)
    data: Mapped[dict] = mapped_column(type_=JSON, index=True)


class FSRSTable(Base):
    """Table for scheduling data (FSRS)."""

    __tablename__ = TableNames.FSRS.value

    card_id: Mapped[str] = mapped_column(
        ForeignKey(f"{TableNames.TEST_CARDS.value}.card_id"),
        primary_key=True,
        index=True,
    )

    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=False), index=True)
    fsrs_data: Mapped[dict] = mapped_column(type_=JSON)


class RecentMistakesTable(Base):
    """Table recording recent mistakes."""

    __tablename__ = "recent_mistakes"

    card_id: Mapped[str] = mapped_column(
        ForeignKey(f"{TableNames.TEST_CARDS.value}.card_id"),
        primary_key=True,
    )

    mistake_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), index=True
    )


class DbManagerBase:
    """Base database manager."""

    def __init__(self, connection_uri: str) -> None:
        self.connection_uri = connection_uri
        debug = False
        self.engine = create_engine(connection_uri, echo=debug)

    def create_database(self) -> None:
        """Creates database."""
        Base.metadata.create_all(self.engine)
