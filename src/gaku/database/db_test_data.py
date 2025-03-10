"""Test data related database functionality."""

import json
import logging
from typing import List, Optional, Union, Sequence
from pathlib import Path

from sqlalchemy import (
    select,
    Integer,
    func,
    cast,
    String,
    Select,
)
from sqlalchemy.orm import (
    Session,
)
from sqlalchemy.engine import ScalarResult


from .db_schema import (
    DbManagerBase,
    CardSourceTable,
    CardSourceLinkTable,
    TestCardsTable,
    FSRSTable,
)
from ..api_types import CardFilter, CardSourceLink
from .. import card_types


class TestEntryManager(DbManagerBase):
    """Test data database manager."""

    def __init__(self, connection_uri: str):
        super().__init__(connection_uri)

    def import_cards(
        self,
        cards: list[card_types.TestCardTypes],
    ) -> None:
        """Imports cards from json file into database."""

        with Session(self.engine) as session:
            highest_position = self.get_card_highest_position() + 1
            cards_db = []
            for pos, card in enumerate(cards):
                if isinstance(
                    card,
                    (
                        card_types.VocabCard,
                        card_types.KanjiCard,
                        card_types.RadicalCard,
                        card_types.QuestionCard,
                        card_types.OnomatopoeiaCard,
                    ),
                ):
                    key = card.writing
                elif isinstance(card, card_types.MultiCard):
                    card.update_writing()
                    key = card.writing
                else:
                    raise ValueError(f"Card type {type(card)} not supported")
                cards_db.append(
                    TestCardsTable(
                        card_id=card.card_id,
                        position=highest_position + pos,
                        key=key,
                        card_type=card.card_type.value,
                        data=card.model_dump(mode="json"),
                    )
                )
            session.add_all(cards_db)

            session.commit()

    def export_cards(self, export_path: Path) -> None:
        """Exports card into json file."""

        if export_path.exists():
            raise FileExistsError(
                "Export file already exists, cannot export. Please use different exkport path."
            )
        with open(export_path, "w", encoding="utf-8") as export_file:
            db_cards = self.get_cards_any_state()
            export = []
            for card in db_cards:
                card_type = card.card_type.value
                export.append(
                    {"card_type": card_type, "card_data": card.model_dump(mode="json")}
                )
            export_file.write(json.dumps(export, indent=2, ensure_ascii=False))

    # generate cards from search query results
    def generate_cards_from_scalar(
        self, card_rows: ScalarResult[TestCardsTable]
    ) -> List[card_types.TestCardTypes]:
        """Generates cards from search query results."""
        with Session(self.engine) as session:
            # get all card data
            card_entries = []
            for card in card_rows:
                logging.info(f"Adding card {card.position} - {card.key}")
                card_entries.append(card.data)

            # handle multi cards
            for entry in card_entries:
                if entry["card_type"] == card_types.CardType.MULTI_CARD:
                    # replace the cards in it with the current cards
                    # using card_ids
                    card_ids = entry["card_ids"]
                    entry["cards"] = [
                        nested_card.data
                        for nested_card in session.execute(
                            select(TestCardsTable).where(
                                TestCardsTable.card_id.in_(card_ids)
                            )
                        ).scalars()
                    ]

            # create cards from json data
            card_results = [
                card_types.create_card_from_json(card_data)
                for card_data in card_entries
            ]
            return card_results

    def get_cards_any_state(
        self,
        filter: Optional[CardFilter] = None,
    ) -> List[card_types.TestCardTypes]:
        """Returns cards matching filter and ignoring FSRS data."""
        with Session(self.engine) as session:
            card_select = select(TestCardsTable).order_by(TestCardsTable.position)
            if filter is not None:
                card_select = self.apply_card_filter_select(card_select, filter)
            return self.generate_cards_from_scalar(session.scalars(card_select))

    def get_new_cards(self, filter: CardFilter) -> List[card_types.TestCardTypes]:
        """Returns all cards that have not been tested yet
        and so don't have any FSRS data.
        """
        logging.info(f"Getting new cards with filter {filter}")
        with Session(self.engine) as session:
            cards_select = self.apply_card_filter_select(
                select(TestCardsTable)
                .order_by(TestCardsTable.position)
                .join(FSRSTable, isouter=True)
                .where(
                    FSRSTable.card_id
                    == None  # noqa: E711  # cannot use is None for sqlalchemy
                ),
                filter,
            )

            return self.generate_cards_from_scalar(session.scalars(cards_select))

    def get_num_new_cards(
        self,
        filter: CardFilter,
    ) -> int:
        """Returns number of card that were not yet studied."""
        # disable the limits for counting
        filter.start_index = None
        filter.num_cards = None

        with Session(self.engine) as session:
            cards_select = (
                select(TestCardsTable)
                .order_by(TestCardsTable.position)
                .join(FSRSTable, isouter=True)
                .where(
                    FSRSTable.card_id
                    == None  # noqa: E711  # cannot use is None for sqlalchemy
                )
            )
            cards_select = self.apply_card_filter_select(cards_select, filter)

            num_new_cards = session.scalar(
                select(func.count()).select_from(cards_select.subquery())
            )
            logging.info(f"Select result: {num_new_cards}")
            if not isinstance(num_new_cards, int):
                raise RuntimeError("Could not count the new cards")

            return num_new_cards

    def get_card_highest_position(self) -> int:
        """Returns current highest position in card table.
        Used for adding cards to keep the ordering.
        """
        with Session(self.engine) as session:
            highest_position = (
                session.query(TestCardsTable.position)
                .order_by(TestCardsTable.position.desc())
                .first()
            )
            return highest_position[0] if highest_position is not None else 0

    def add_card(
        self,
        card: Union[card_types.TestCardTypes],
    ) -> None:
        """Adds a card to database."""
        self.import_cards([card])

    def update_card(
        self,
        card: Union[card_types.TestCardTypes],
    ) -> None:
        """Updates card data in database."""
        with Session(self.engine) as session:
            card_db = (
                session.query(TestCardsTable)
                .filter(TestCardsTable.card_id == card.card_id)
                .first()
            )
            if card_db is None:
                raise ValueError(f"Card with id {card.card_id} not found")
            # verify that card type is the same
            if not card.card_type == card_types.CardType(card_db.card_type):
                raise ValueError(
                    f"Card type {card.card_type} does not match the card type in the database {card_db.card_type}"
                )
            if isinstance(
                card,
                (
                    card_types.VocabCard,
                    card_types.KanjiCard,
                    card_types.RadicalCard,
                    card_types.QuestionCard,
                    card_types.OnomatopoeiaCard,
                ),
            ):
                card_key = card.writing
            elif isinstance(card, card_types.MultiCard):
                card.update_writing()
                card_key = card.writing
            else:
                raise ValueError(f"Card type {type(card)} not supported")
            if card.card_type.value != card_db.card_type:
                raise ValueError(
                    f"Card type {card.card_type.value} does not match the card type in the database {card_db.card_type}"
                )
            card_db.key = card_key
            # card_db.dictionary_id = card.dictionary_id
            card_db.data = card.model_dump(mode="json")
            session.commit()

    def delete_card(self, card_id: str) -> None:
        """Deletes a card with specified card id.
        Also removes attached source links and FSRS data.
        """
        with Session(self.engine) as session:
            # delete card
            card_db = (
                session.query(TestCardsTable)
                .filter(TestCardsTable.card_id == card_id)
                .first()
            )
            if card_db is None:
                raise ValueError(f"Card with id {card_id} not found")
            session.delete(card_db)

            # delete card source links
            session.query(CardSourceLinkTable).filter(
                CardSourceLinkTable.card_id == card_id
            ).delete()

            # delete fsrs data
            session.query(FSRSTable).filter(FSRSTable.card_id == card_id).delete()

            session.commit()

    def get_card_source_link_highest_position(self, card_source_id: str) -> int:
        """Returns highest position of a card."""
        # TOOD: clarify purpose
        with Session(self.engine) as session:
            highest_position = (
                session.query(CardSourceLinkTable)
                .where(CardSourceLinkTable.source_id == card_source_id)
                .order_by(CardSourceLinkTable.position.desc())
                .first()
            )
            return highest_position.position if highest_position is not None else 0

    def add_card_source_link(self, card_id: str, source_id: str) -> None:
        """Adds source link for card id."""
        with Session(self.engine) as session:
            # only add link if it does not exist
            source_link = (
                session.query(CardSourceLinkTable)
                .filter(
                    CardSourceLinkTable.card_id == card_id,
                    CardSourceLinkTable.source_id == source_id,
                )
                .first()
            )
            if source_link is not None:
                return
            highest_position = self.get_card_source_link_highest_position(source_id)
            session.add(
                CardSourceLinkTable(
                    card_id=card_id, source_id=source_id, position=highest_position + 1
                )
            )
            session.commit()

    def get_card_sources(self, card_id: str) -> List[card_types.CardSource]:
        """Returns a list of card sources for a card id."""
        with Session(self.engine) as session:
            sources = (
                session.query(CardSourceTable)
                .join(CardSourceLinkTable)
                .filter(CardSourceLinkTable.card_id == card_id)
                .all()
            )
            return [
                card_types.CardSource(
                    source_id=source.source_id,
                    source_name=source.source_name,
                    source_section=source.source_section,
                )
                for source in sources
            ]

    def get_vocab_entries_by_key(self, key: str) -> List[card_types.VocabCard]:
        """Returns Vocab card for specified key."""
        with Session(self.engine) as session:
            cards = (
                session.query(TestCardsTable)
                .filter(
                    TestCardsTable.key == key,
                    TestCardsTable.card_type == card_types.CardType.VOCABULARY.value,
                )
                .all()
            )
            return [card_types.VocabCard(**card.data) for card in cards]

    def get_vocab_entry_by_dictionary_id(
        self, vocab: str, dictionary_id: Optional[int] = None
    ) -> Optional[card_types.VocabCard]:
        """Returns Vocab card for a specified dictionary id."""
        # dictionary_id is unique identifier for JMdict or other dictionary
        # and is stored in the vocab card
        with Session(self.engine) as session:
            card = (
                session.query(TestCardsTable)
                .filter(
                    TestCardsTable.key == vocab,
                    TestCardsTable.card_type == card_types.CardType.VOCABULARY.value,
                    func.json_extract(TestCardsTable.data, "$.dictionary_id").cast(
                        Integer
                    )
                    == dictionary_id,
                )
                .first()
            )
            if card is None:
                logging.warning(
                    f"Vocab card with key {vocab} and dictionary_id {dictionary_id} not found"
                )
                return None

            logging.info(
                f"Vocab card with key {vocab} and dictionary_id {dictionary_id}: {card}"
            )
            return card_types.VocabCard(**card.data)

    def get_multi_card_data(self, card_data: dict) -> dict:
        """Updates nested card data for a MultiCard."""
        with Session(self.engine) as session:
            card_ids = card_data["card_ids"]
            cards = (
                session.query(TestCardsTable)
                .filter(TestCardsTable.card_id.in_(card_ids))
                .all()
            )
            card_data["cards"] = [card.data for card in cards]
            return card_data

    def get_card_by_key(
        self, key: str, card_type: card_types.CardType
    ) -> Optional[card_types.TestCardTypes]:
        """Returns card for a specified combination of key and card type."""
        with Session(self.engine) as session:
            card = (
                session.query(TestCardsTable)
                .filter(
                    TestCardsTable.key == key,
                    TestCardsTable.card_type == card_type.value,
                )
                .first()
            )
            logging.info(f"Card with key {key} and type {card_type}: {card}")
            if card is None:
                return None
            card_data = card.data
            if card.data["card_type"] == card_types.CardType.MULTI_CARD:
                card_data = self.get_multi_card_data(card.data)

            return card_types.create_card_from_json(card_data)

    def get_card_by_card_id(self, card_id: str) -> Optional[card_types.TestCardTypes]:
        """Returns card for a specified card id."""
        with Session(self.engine) as session:
            card = (
                session.query(TestCardsTable)
                .filter(TestCardsTable.card_id == card_id)
                .first()
            )
            if card is None:
                return None
            card_data = card.data
            if card.data["card_type"] == card_types.CardType.MULTI_CARD:
                card_data = self.get_multi_card_data(card.data)

            return card_types.create_card_from_json(card_data)

    def get_card_source_ids(self, card_id: str) -> List[str]:
        """Provides list of source ids for a card."""
        with Session(self.engine) as session:
            source_ids = (
                session.query(CardSourceLinkTable.source_id)
                .filter(CardSourceLinkTable.card_id == card_id)
                .all()
            )
            return [source_id for source_id, in source_ids]

    def delete_card_source_link(self, card_id: str, source_id: str) -> None:
        """Removes source link for a card."""
        with Session(self.engine) as session:
            source_link = (
                session.query(CardSourceLinkTable)
                .filter(
                    CardSourceLinkTable.card_id == card_id,
                    CardSourceLinkTable.source_id == source_id,
                )
                .first()
            )
            if source_link is None:
                raise ValueError(
                    f"Card source link with card_id {card_id} and source_id {source_id} not found"
                )
            session.delete(source_link)
            session.commit()

    def delete_all_card_source_links(self, card_id: str) -> None:
        """Removes all source links for a card."""
        with Session(self.engine) as session:
            session.query(CardSourceLinkTable).filter(
                CardSourceLinkTable.card_id == card_id
            ).delete()
            session.commit()

    def add_cards(self, cards: Sequence[card_types.TestCardTypes]) -> None:
        """Batch inserts cards into the database."""
        with Session(self.engine) as session:
            highest_position = self.get_card_highest_position() + 1
            cards_db = []
            for pos, card in enumerate(cards):
                if isinstance(
                    card,
                    (
                        card_types.VocabCard,
                        card_types.KanjiCard,
                        card_types.RadicalCard,
                        card_types.QuestionCard,
                        card_types.OnomatopoeiaCard,
                    ),
                ):
                    key = card.writing
                elif isinstance(card, card_types.MultiCard):
                    card.update_writing()
                    key = card.writing
                else:
                    raise ValueError(f"Card type {type(card)} not supported")
                cards_db.append(
                    TestCardsTable(
                        card_id=card.card_id,
                        dictionary_id=card.dictionary_id,
                        position=highest_position + pos,
                        key=key,
                        card_type=card.card_type.value,
                        data=card.model_dump(mode="json"),
                    )
                )
            session.add_all(cards_db)
            session.commit()

    def add_card_source_links(self, source_links: list[CardSourceLink]) -> None:
        """Batch inserts card source links into the database."""
        logging.info(f"Batch add source links: {source_links}")
        with Session(self.engine) as session:
            # dict[source_id, highest position]
            positions: dict[str, int] = {}
            new_links = []
            for link in source_links:
                exists = session.scalar(
                    select(CardSourceLinkTable.card_id)
                    .where(CardSourceLinkTable.card_id == link.card_id)
                    .where(CardSourceLinkTable.source_id == link.source_id)
                )
                logging.info(f"Exists: {exists}")
                if exists is None:
                    if link.source_id not in positions:
                        highest_position = self.get_card_source_link_highest_position(
                            link.source_id
                        )
                        positions[link.source_id] = highest_position

                    positions[link.source_id] += 1
                    logging.info(
                        f"Adding new source link {link.source_id} for card:{link.card_id}"
                    )
                    new_links.append(
                        CardSourceLinkTable(
                            position=positions[link.source_id],
                            card_id=link.card_id,
                            source_id=link.source_id,
                        )
                    )

            session.add_all(new_links)
            session.commit()

    def apply_card_filter_select(
        self, card_select: Select, filter: CardFilter
    ) -> Select:
        """Applies card selection filter to current select."""
        if filter.card_sources:
            source_ids = [source.source_id for source in filter.card_sources]
            card_select = card_select.filter(
                TestCardsTable.card_id.in_(
                    select(CardSourceLinkTable.card_id).where(
                        CardSourceLinkTable.source_id.in_(source_ids)
                    )
                )
            )
        if filter.card_types:
            card_select = card_select.filter(
                TestCardsTable.card_type.in_(
                    [card_type.value for card_type in filter.card_types]
                )
            )
        if filter.search_text:
            logging.debug(f"Searching for text {filter.search_text}")
            # converting to json string with ensure_ascii=True, because
            # the database search is dumb and fails to convert the stored data back to utf-8
            # and the search fails
            # since the text is stored using unicode escape sequences
            # the json.dumps converts the search to working format
            escaped_text = json.dumps(filter.search_text, ensure_ascii=True)[1:-1]
            card_select = card_select.filter(
                cast(TestCardsTable.data, String).ilike(f"%{escaped_text}%")
            )
        if filter.num_cards is not None and filter.num_cards > 0:
            card_select = card_select.limit(filter.num_cards)
        if filter.start_index is not None:
            card_select = card_select.offset(filter.start_index)
        return card_select

    def get_cards_by_text(self, filter: CardFilter) -> List[card_types.TestCardTypes]:
        """Returns cards that contain given text in their data."""
        with Session(self.engine) as session:
            cards_select = self.apply_card_filter_select(
                select(TestCardsTable),
                filter,
            )

            return self.generate_cards_from_scalar(session.scalars(cards_select))

    def get_num_cards_any_state(self, filter: CardFilter) -> int:
        """Get the number of cards matching filter independent on FSRS state."""
        #  disable the limits for counting
        filter.num_cards = None
        filter.start_index = None

        with Session(self.engine) as session:
            card_select = self.apply_card_filter_select(
                select(TestCardsTable.card_id), filter
            )

            num_cards = session.scalar(
                select(func.count()).select_from(card_select.subquery())
            )
            if not isinstance(num_cards, int):
                raise RuntimeError("Could not count the cards")

        return num_cards
