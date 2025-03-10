"""Database for the dictionary."""

import json
import logging
from enum import Enum
from typing import Optional

from sqlalchemy import (
    ForeignKey,
    String,
    JSON,
    create_engine,
    Integer,
    select,
    func,
    ScalarResult,
    cast,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    Session,
    relationship,
)

from .dictionary import VocabularyMeaning, Radical, Kanji, DictionaryEntry
from .question import AnswerText
from .card_types import OnomatopoeiaCard, OnomatopoeiaDefinition

# new style Union using a pipe operator
json_list = list[int] | list[str]


class DictionaryTableNames(Enum):
    """Dictionary name mapping."""

    VOCAB_DICTIONARY = "vocab_dictionary"
    VOCAB_KANJI_WRITING = "vocab_kanji_writing"
    VOCAB_KANA_WRITING = "vocab_kana_writing"
    VOCAB_MEANINGS = "vocab_meanings"
    VOCAB_MEANING = "vocab_meaning"
    KANJI_DICTIONARY = "kanji_dictionary"
    RADICAL_DICTIONARY = "radical_dictionary"
    ONO_DICTIONARY = "ono_dictionary"
    ONO_DEFINITIONS = "ono_definitions"


class DictionaryBase(DeclarativeBase):
    """Base for dictionary database tables."""

    pass


class VocabDictionaryTable(DictionaryBase):
    """Vocabulary dictionary table."""

    __tablename__ = DictionaryTableNames.VOCAB_DICTIONARY.value

    ent_seq: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # kanji_elements: Mapped[list[str]] = mapped_column(JSON, index=True)
    # reading_elements: Mapped[list[str]] = mapped_column(JSON, index=True)
    kanji_children: Mapped[list["VocabKanjiWritingTable"]] = relationship(
        back_populates="vocab_kanji_parent"
    )
    kana_children: Mapped[list["VocabKanaWritingTable"]] = relationship(
        back_populates="vocab_kana_parent"
    )
    meaning_children: Mapped[list["VocabMeaningsTable"]] = relationship(
        back_populates="vocab_meaning_parent"
    )


class VocabKanjiWritingTable(DictionaryBase):
    """Table for vocabulary entry writing (kanji form)."""

    __tablename__ = DictionaryTableNames.VOCAB_KANJI_WRITING.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    ent_seq: Mapped[int] = mapped_column(
        ForeignKey(f"{DictionaryTableNames.VOCAB_DICTIONARY.value}.ent_seq")
    )
    kanji_writing: Mapped[str] = mapped_column(String, index=True)
    vocab_kanji_parent: Mapped["VocabDictionaryTable"] = relationship(
        back_populates="kanji_children"
    )


class VocabKanaWritingTable(DictionaryBase):
    """Table for vocabulary entry kana writing."""

    __tablename__ = DictionaryTableNames.VOCAB_KANA_WRITING.value

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    ent_seq: Mapped[int] = mapped_column(
        ForeignKey(f"{DictionaryTableNames.VOCAB_DICTIONARY.value}.ent_seq")
    )
    kana_writing: Mapped[str] = mapped_column(String, index=True)
    vocab_kana_parent: Mapped["VocabDictionaryTable"] = relationship(
        back_populates="kana_children"
    )


class VocabMeaningsTable(DictionaryBase):
    """Table for vocabulary meaning grouping."""

    __tablename__ = DictionaryTableNames.VOCAB_MEANINGS.value

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    ent_seq: Mapped[int] = mapped_column(
        ForeignKey(f"{DictionaryTableNames.VOCAB_DICTIONARY.value}.ent_seq"), index=True
    )
    part_of_speech: Mapped[str]
    children: Mapped[list["VocabMeaningTable"]] = relationship(back_populates="parent")
    vocab_meaning_parent: Mapped["VocabDictionaryTable"] = relationship(
        back_populates="meaning_children"
    )


class VocabMeaningTable(DictionaryBase):
    """Table for vocabulary meaning entries."""

    __tablename__ = DictionaryTableNames.VOCAB_MEANING.value

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    meanings_id: Mapped[int] = mapped_column(
        ForeignKey(f"{DictionaryTableNames.VOCAB_MEANINGS.value}.id"), index=True
    )
    parent: Mapped["VocabMeaningsTable"] = relationship(back_populates="children")
    meaning: Mapped[str] = mapped_column(String, index=True)


class KanjiDictionaryTable(DictionaryBase):
    """Table for Kanji dictionary."""

    __tablename__ = DictionaryTableNames.KANJI_DICTIONARY.value

    literal: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    codepoints: Mapped[dict[str, str]] = mapped_column(JSON)
    ucs_codepoint: Mapped[Optional[int]]
    radicals: Mapped[dict[str, int]] = mapped_column(JSON)
    grade: Mapped[Optional[int]]
    stroke_count: Mapped[list[int]] = mapped_column(JSON)
    variants: Mapped[dict[str, str]] = mapped_column(JSON)
    frequency: Mapped[Optional[int]]
    radical_names: Mapped[list[str]] = mapped_column(JSON)
    jlpt: Mapped[Optional[int]]
    meanings: Mapped[list[str]] = mapped_column(JSON, index=True)
    readings: Mapped[dict[str, list[str]]] = mapped_column(JSON, index=True)
    nanori: Mapped[list[str]] = mapped_column(JSON)


class RadicalDictionaryTable(DictionaryBase):
    """Table for Radical dictionary."""

    __tablename__ = DictionaryTableNames.RADICAL_DICTIONARY.value

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    stroke: Mapped[Optional[int]]
    radical: Mapped[str] = mapped_column(String, index=True)
    meaning: Mapped[str] = mapped_column(String, index=True)
    reading_j: Mapped[str]
    reading_r: Mapped[Optional[str]]
    position_j: Mapped[Optional[str]]
    position_r: Mapped[Optional[str]]


class OnoDictionaryTable(DictionaryBase):
    """Table for Onomatopoeia dictionary."""

    __tablename__ = DictionaryTableNames.ONO_DICTIONARY.value

    writing: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    kana_writing: Mapped[list[str]] = mapped_column(JSON, index=True)
    definitions: Mapped[list[dict]] = mapped_column(JSON, index=True)


class DictionaryManager:
    """Manager for working with the dictionary database and data."""

    def __init__(self, connection_uri: str) -> None:
        self.connection_uri = connection_uri
        self.engine = create_engine(connection_uri, echo=False)

    def create_database(self) -> None:
        """Creates database."""
        DictionaryBase.metadata.create_all(self.engine)

    def add_vocabulary(self, vocabulary: list[DictionaryEntry]) -> None:
        """Adds vocabulary entries to database."""
        num_items = len(vocabulary)
        with Session(self.engine) as session:
            for idx, vocab_item in enumerate(vocabulary):
                if idx % 1000 == 0:
                    print(f"Processing {idx}/{num_items}")
                vocab_entry = VocabDictionaryTable(
                    ent_seq=vocab_item.ent_seq,
                )
                session.add(vocab_entry)

                for kanji in vocab_item.kanji_elements:
                    kanji_entry = VocabKanjiWritingTable(kanji_writing=kanji)
                    vocab_entry.kanji_children.append(kanji_entry)
                for kana in vocab_item.reading_elements:
                    kana_entry = VocabKanaWritingTable(kana_writing=kana)
                    vocab_entry.kana_children.append(kana_entry)
                for meanings in vocab_item.meanings:
                    meanings_entry = VocabMeaningsTable(
                        part_of_speech=meanings.part_of_speech,
                    )
                    vocab_entry.meaning_children.append(meanings_entry)

                    for meaning in meanings.meanings:
                        meanings_entry.children.append(
                            VocabMeaningTable(meaning=meaning)
                        )
            session.commit()

    def add_kanji(self, kanji: list[Kanji]) -> None:
        """Adds Kanji to database."""
        with Session(self.engine) as session:
            for item in kanji:
                session.add(KanjiDictionaryTable(**item.model_dump(mode="json")))
            session.commit()

    def add_radicals(self, radicals: list[Radical]) -> None:
        """Adds Radicals to database."""
        with Session(self.engine) as session:
            for radical in radicals:
                session.add(RadicalDictionaryTable(**radical.model_dump(mode="json")))
            session.commit()

    def get_radical(self, radical: str) -> Optional[Radical]:
        """Find radical based on radical character.

        Parameters
        ----------
        radical: str
            The radical character to search for.

        Returns
        -------
        Optional[Radical]
            The Radical object if found, None otherwise.
        """
        with Session(self.engine) as session:
            entries = (
                session.execute(
                    select(RadicalDictionaryTable).where(
                        RadicalDictionaryTable.radical == radical
                    )
                )
                .scalars()
                .fetchall()
            )

            if len(entries) == 0:
                return None

            if len(entries) > 1:
                logging.warning(f"Got multiple entries for radical search: {entries}")

            entry = entries[0]

            return Radical(
                id=entry.id,
                stroke=entry.stroke,
                radical=entry.radical,
                meaning=entry.meaning,
                reading_j=entry.reading_j,
                reading_r=entry.reading_r,
                position_j=entry.position_j,
                position_r=entry.position_r,
            )

    def get_radical_by_id(self, radical_id: int) -> Optional[Radical]:
        """Gets radical by radical id.

        Parameters
        ----------
        radical_id: int
            Radical id to search for.

        Returns
        -------
        Optional[Radical]
            The Radical object if found, None otherwise.
        """

        with Session(self.engine) as session:
            entry = session.execute(
                select(RadicalDictionaryTable).where(
                    RadicalDictionaryTable.id == radical_id
                )
            ).scalar()

            if entry is None:
                return None

            return Radical(
                id=entry.id,
                stroke=entry.stroke,
                radical=entry.radical,
                meaning=entry.meaning,
                reading_j=entry.reading_j,
                reading_r=entry.reading_r,
                position_j=entry.position_j,
                position_r=entry.position_r,
            )

    def get_num_radicals(self) -> int:
        """Get number of radicals in database.

        Returns
        -------
        int
            Number of radicals currently in database.

        Raises
        ------
        RuntimeError
            In case the radicals could not be counted.
        """

        with Session(self.engine) as session:
            num_radicals = session.scalar(select(func.count(RadicalDictionaryTable.id)))
            if num_radicals is None:
                raise RuntimeError("Could not count the radicals")
            return num_radicals

    def get_kanji(self, character: str) -> Optional[Kanji]:
        """Gets kanji by character.

        Returns
        -------
        Optional[Kanji]
            The Kanji object or None if not found
        """
        with Session(self.engine) as session:
            kanji = session.execute(
                select(KanjiDictionaryTable).where(
                    KanjiDictionaryTable.literal == character
                )
            ).scalar()

            if kanji is None:
                return None

            return Kanji(
                literal=kanji.literal,
                codepoints=kanji.codepoints,
                ucs_codepoint=kanji.ucs_codepoint,
                radicals=kanji.radicals,
                grade=kanji.grade,
                stroke_count=kanji.stroke_count,
                variants=kanji.variants,
                frequency=kanji.frequency,
                radical_names=kanji.radical_names,
                jlpt=kanji.jlpt,
                meanings=kanji.meanings,
                readings=kanji.readings,
                nanori=kanji.nanori,
            )

    def get_vocabulary_by_id(self, dictionary_id: int) -> Optional[DictionaryEntry]:
        """Get vocabulary by dictionary id.

        Parameters
        ----------
        dictionary_id: int
            Id of the dictionary entry.

        Returns
        -------
        Optional[DictionaryEntry]
            DictionaryEntry object or None if not found.
        """
        with Session(self.engine) as session:
            entries = session.execute(
                select(VocabDictionaryTable).where(
                    VocabDictionaryTable.ent_seq == dictionary_id
                )
            ).scalars()

            if entries is None:
                return None

            return self.create_vocab_list(entries)[0]

    def create_meaning_list(self, meanings: VocabMeaningsTable) -> list[str]:
        """Creates meanings list for vocabulary."""
        with Session(self.engine) as session:
            meaning_entries = session.execute(
                select(VocabMeaningTable).where(
                    VocabMeaningTable.meanings_id == meanings.id
                )
            ).scalars()

            return [meaning.meaning for meaning in meaning_entries]

    def create_vocab_list(
        self, vocab_rows: ScalarResult[VocabDictionaryTable]
    ) -> list[DictionaryEntry]:
        """Creates a list of vocabulary entries."""
        with Session(self.engine) as session:
            vocab: list[DictionaryEntry] = []
            for entry in vocab_rows:
                meanings_entries = session.execute(
                    select(VocabMeaningsTable).where(
                        VocabMeaningsTable.ent_seq == entry.ent_seq
                    )
                ).scalars()

                meanings = [
                    VocabularyMeaning(
                        part_of_speech=meaning.part_of_speech,
                        meanings=self.create_meaning_list(meaning),
                    )
                    for meaning in meanings_entries
                ]

                kanji_entries = session.execute(
                    select(VocabKanjiWritingTable).where(
                        VocabKanjiWritingTable.ent_seq == entry.ent_seq
                    )
                ).scalars()
                kanji = [kanji.kanji_writing for kanji in kanji_entries]

                kana_entries = session.execute(
                    select(VocabKanaWritingTable).where(
                        VocabKanaWritingTable.ent_seq == entry.ent_seq
                    )
                ).scalars()
                kana = [kana.kana_writing for kana in kana_entries]

                vocab.append(
                    DictionaryEntry(
                        ent_seq=entry.ent_seq,
                        kanji_elements=kanji,
                        reading_elements=kana,
                        meanings=meanings,
                    )
                )
        return vocab

    def get_vocabulary_by_kanji_writing(self, kanji: str) -> list[DictionaryEntry]:
        """Finds vocabulary entries that use provided kanji writing
        (meaning the writing using kanji, not only kana, if kanji are used).

        Parameters
        ----------
        kanji: str
            Kanji writing to search for.

        Returns
        -------
        list[DictionaryEntry]
            List of DictionaryEntry object that match the search criteria
        """

        with Session(self.engine) as session:
            # kanji = json.dumps(kanji.casefold(), ensure_ascii=True)[1:-1]
            entries = session.execute(
                select(VocabDictionaryTable)
                .join(VocabKanjiWritingTable)
                .where(VocabKanjiWritingTable.kanji_writing == kanji)
            ).scalars()

            return self.create_vocab_list(entries)

    def get_vocabulary_by_kana_writing(self, reading: str) -> list[DictionaryEntry]:
        """Finds vocabulary entries using kana writing.

        Parameters
        ----------
        reading: str
            Kana writing to search for.

        Returns
        -------
        list[DictionaryEntry]
            List of DictionaryEntry object that match the search criteria
        """

        with Session(self.engine) as session:
            # reading = json.dumps(reading.casefold(), ensure_ascii=True)[1:-1]
            entries = session.execute(
                select(VocabDictionaryTable)
                .join(VocabKanaWritingTable)
                .where(VocabKanaWritingTable.kana_writing == reading)
            ).scalars()

            return self.create_vocab_list(entries)

    def get_vocabulary_by_meaning(self, meaning: str) -> list[DictionaryEntry]:
        """Finds vocabulary entries using provided meaning.

        Parameters
        ----------
        meaning: str
            Meaning to search for.

        Returns
        -------
        list[DictionaryEntry]
            List of DictionaryEntry object that match the search criteria
        """

        with Session(self.engine) as session:
            # meaning = json.dumps(meaning.casefold(), ensure_ascii=True)[1:-1]
            entries = session.execute(
                select(VocabDictionaryTable)
                .join(VocabMeaningsTable)
                .join(VocabMeaningTable)
                .where(VocabMeaningTable.meaning == meaning)
            ).scalars()

            return self.create_vocab_list(entries)

    def get_num_vocabulary(self) -> int:
        """Get number of vocabulary entries in database.

        Returns
        -------
        int
            Number of vocabulary currently in database.

        Raises
        ------
        RuntimeError
            In case the vocabulary could not be counted.
        """

        with Session(self.engine) as session:
            num_vocab = session.scalar(select(func.count(VocabDictionaryTable.ent_seq)))
            if num_vocab is None:
                raise RuntimeError("Could not count the vocabulary")
            return num_vocab

    def add_onomatopoeia(self, onomatopoeia: list[dict]) -> None:
        """Adds Onomatopoeia to database."""
        with Session(self.engine) as session:
            for item in onomatopoeia:
                kana_writing: list[str] = item["hiragana"] + item["katakana"]
                definitions: list[dict] = item["definition"]
                literal: str = item["literal"]
                session.add(
                    OnoDictionaryTable(
                        writing=literal,
                        kana_writing=kana_writing,
                        definitions=definitions,
                    )
                )
            session.commit()

    def get_ono_by_kana(self, kana: str) -> list[OnomatopoeiaCard]:
        """Finds onomatopoeia entry by Kana (Hiragana or Katakana).

        Parameters
        ----------
        kana: str
            The kana to search for

        Returns
        -------
        list[OnoCard]
            The list of foun entries as OnoCard
        """
        with Session(self.engine) as session:
            # converting to json string with ensure_ascii=True, because
            # the database search is dumb and fails to convert the stored data back to utf-8
            # and the search fails
            # since the text is stored using unicode escape sequences
            # the json.dumps converts the search to working format
            escaped_text = json.dumps(kana, ensure_ascii=True)[1:-1]
            ono_items = session.scalars(
                select(OnoDictionaryTable).filter(
                    cast(OnoDictionaryTable.kana_writing, String).ilike(
                        f"%{escaped_text}%"
                    )
                )
            )

            cards = [
                OnomatopoeiaCard(
                    writing=item.writing,
                    kana_writing=item.kana_writing,
                    definitions=[
                        OnomatopoeiaDefinition(
                            equivalent=[
                                AnswerText(answer_text=equivalent)
                                for equivalent in definition["equivalent"]
                            ],
                            meaning=AnswerText(answer_text=definition["meaning"]),
                        )
                        for definition in item.definitions
                    ],
                )
                for item in ono_items
            ]
            return cards
