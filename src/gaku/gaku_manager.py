"""Manager for all Gaku functionality."""

import datetime
import json
import logging
from pathlib import Path
from typing import Optional

from .database import DbManager
from .card_types import (
    TestQuestion,
    VocabCard,
    KanjiCard,
    RadicalCard,
    CardType,
    CardSource,
    create_card_from_json,
    VocabularyMeaningEntry,
    Answer,
    AnswerGroup,
    AnswerType,
    TestCardTypes,
    MultiCard,
    AnswerText,
)
from .test_session import TestSession
from .dictionary import (
    RadicalDictionary,
    KanjiDictionary,
    JapaneseDictionary,
    DictionaryEntry,
    Kanji,
    Radical,
)
from .db_dictionary import DictionaryManager
from .api_types import (
    GeneratedImports,
    ImportItem,
    StartTestRequest,
    CardFilter,
    CardSourceLink,
)


class GakuManager:
    """Manages all the Gaku functionality."""

    def __init__(self, workdir: Path, resource_dir: Optional[Path] = None) -> None:
        self.workdir = workdir
        self.resource_dir = resource_dir or Path("resources")
        workdir.mkdir(exist_ok=True, parents=True)

        self.db_file: Path = workdir / "cards.db"
        self.db_connection: str = f"sqlite:///{str(self.db_file.resolve())}"
        self.db: DbManager = DbManager(self.db_connection)
        if not self.db_file.exists():
            self.db.create_database()

        self.test_session: Optional[TestSession] = None

        self.db_dictionary_file = workdir / "dictionary.db"
        dictionary_exists = self.db_dictionary_file.exists()
        self.dictionary: DictionaryManager = DictionaryManager(
            f"sqlite:///{str(self.db_dictionary_file.resolve())}"
        )
        if not dictionary_exists:
            self.create_dictionary_db()

    def create_dictionary_db(self) -> None:
        """Creates dictionary database."""
        # import the dictionaries
        logging.info("Importing dictionaries, this might take a few minutes")
        radical_dict = RadicalDictionary(self.resource_dir / "kanji-radicals.csv")
        kanji_dict = KanjiDictionary(self.resource_dir / "kanjidic2.xml")
        japanese_dict = JapaneseDictionary(self.resource_dir / "JMdict_e.xml")

        # create database
        self.dictionary.create_database()
        self.dictionary.add_radicals(list(radical_dict.radicals.values()))
        self.dictionary.add_kanji(list(kanji_dict.kanji.values()))
        self.dictionary.add_vocabulary(list(japanese_dict.entries.values()))
        logging.info("Finished importing dictionaries")

    def import_cards_from_file(self, import_file: Path) -> None:
        """Imports card into database from a file."""
        with import_file.open("r") as f:
            cards_json = json.load(f)
        cards = [create_card_from_json(card["card_data"]) for card in cards_json]

        self.db.import_cards(cards)

    def export_cards_to_file(self, export_file: Path) -> None:
        """Exports cards from database to file."""
        if export_file.exists():
            raise FileExistsError(f"File {export_file} already exists")

        export_file.parent.mkdir(parents=True, exist_ok=True)
        self.db.export_cards(export_file)

    def get_dictionary_radical_for_kanji(
        self, kanji: KanjiCard
    ) -> Optional[RadicalCard]:
        """Gets radical for a kanji using dictionary."""
        if kanji.radical_id is None:
            return None
        radical = self.dictionary.get_radical_by_id(kanji.radical_id)
        if radical:
            return RadicalCard(
                dictionary_id=radical.id,
                writing=radical.radical,
                meanings=[
                    AnswerText(answer_text=meaning.strip())
                    for meaning in radical.meaning.split(",")
                ],
                reading=radical.reading_j,
            )
        return None

    def add_extra_questions(self, card: TestCardTypes | MultiCard) -> None:
        """Generates extra questions for the cards.

        The cards are created as follows:
        - Vocab: add kanji meanings question
        - Kanji: add radical question
        - Radical: no extra questions
        - MultiCard: no extra questions
        """
        # TODO: precompute the questions and make them available in the card
        if isinstance(card, VocabCard):
            kanji_cards, _new_kanji_cards = self.get_kanji_cards(card.writing)

            if not kanji_cards:
                return
            answers: list[Answer] = []
            for kanji_card in kanji_cards:
                answers.append(
                    Answer(
                        answer_type=AnswerType.ROMAJI,
                        header=f"Kanji {kanji_card.writing} meaning",
                        answers=kanji_card.meanings,
                    )
                )
            card.custom_questions.append(
                TestQuestion(
                    parent_id=card.card_id,
                    header="Kanji meanings for vocab",
                    question=card.writing,
                    hint=", ".join(
                        [meaning.answer_text for meaning in card.meanings[0].meanings]
                    ),
                    answers=[AnswerGroup(answers=answers)],
                )
            )

        elif isinstance(card, KanjiCard):
            radical_card = self.get_dictionary_radical_for_kanji(card)
            if radical_card:
                card.custom_questions.append(
                    TestQuestion(
                        parent_id=card.card_id,
                        header="Radical for kanji",
                        question=card.writing,
                        hint=", ".join(
                            [meaning.answer_text for meaning in card.meanings]
                        ),
                        answers=[
                            AnswerGroup(
                                answers=[
                                    Answer(
                                        answer_type=AnswerType.ROMAJI,
                                        header=f"Radical {radical_card.writing} meaning",
                                        answers=radical_card.meanings,
                                    )
                                ]
                            ),
                        ],
                    )
                )

    def start_test_session(
        self,
        test_setup: StartTestRequest,
    ) -> TestSession:
        """Starts test session ignoring FRSR state."""

        self.test_session = TestSession(
            db=self.db, mark_answers=test_setup.mark_answers
        )
        study_cards = self.db.get_cards_any_state(test_setup)
        if test_setup.generate_extra_questions:
            for card in study_cards:
                self.add_extra_questions(card)

        self.test_session.load(study_cards)
        return self.test_session

    def start_test_session_new_cards(
        self,
        test_setup: StartTestRequest,
    ) -> TestSession:
        """Start test session with new cards."""
        self.test_session = TestSession(
            db=self.db, mark_answers=test_setup.mark_answers, shuffle_questions=False
        )

        study_cards = self.db.get_new_cards(test_setup)

        if test_setup.generate_extra_questions:
            logging.info("Adding extra questions")
            for card in study_cards:
                self.add_extra_questions(card)
        self.test_session.load(study_cards)

        return self.test_session

    def start_test_session_recent_mistakes(
        self,
        test_setup: StartTestRequest,
        timestamp: int,
    ) -> TestSession:
        """Starts test session with recent mistakes."""

        mark_answers = test_setup.mark_answers
        self.test_session = TestSession(db=self.db, mark_answers=mark_answers)
        study_cards = self.db.mistakes_get_mistakes_cards(timestamp, test_setup)
        for card in study_cards:
            self.add_extra_questions(card)
        self.test_session.load(study_cards)

        return self.test_session

    def get_num_matching_new_cards(self, filter: CardFilter) -> int:
        """Get the number of new cards that match the test setup."""
        return self.db.get_num_new_cards(filter)

    def start_test_session_fsrs_due(
        self,
        test_setup: StartTestRequest,
    ) -> TestSession:
        """Start test session with cards that due date in fsrs."""

        self.test_session = TestSession(
            db=self.db, mark_answers=test_setup.mark_answers
        )
        study_cards = self.db.get_fsrs_due_cards(test_setup)
        for card in study_cards:
            self.add_extra_questions(card)
        self.test_session.load(study_cards)

        return self.test_session

    def start_test_session_studied(self, test_setup: StartTestRequest) -> TestSession:
        """Starts test session with studied cards matching the test_setup settings.

        Paramteters
        -----------
        test_setup: StartTestRequest
            Configuration of the test

        Returns
        -------
        TestSession
            New test session with cards matching the setup.
        """

        self.test_session = TestSession(
            db=self.db, mark_answers=test_setup.mark_answers
        )
        study_cards = self.db.get_studied_cards(test_setup)
        for card in study_cards:
            self.add_extra_questions(card)
        self.test_session.load(study_cards)

        return self.test_session

    def get_num_due_cards(self, filter: CardFilter) -> int:
        """Get the number of cards that are due for testing."""
        return self.db.get_num_fsrs_due_cards(filter)

    def get_session_exists(self) -> bool:
        """Checks if there is a test session."""
        return self.test_session is not None

    def get_session_active(self) -> bool:
        """Checks if test session is active."""
        return (
            self.test_session is not None
            and not self.test_session.is_session_finished()
        )

    def find_dictionary_vocab_by_writing(self, query: str) -> list[DictionaryEntry]:
        """Searches vocabulary dictionary by writing (kanji)."""
        return self.dictionary.get_vocabulary_by_kanji_writing(query)

    def find_dictionary_vocab_by_reading(self, query: str) -> list[DictionaryEntry]:
        """Searches vocab dictionary by reading (kana)."""
        return self.dictionary.get_vocabulary_by_kana_writing(query)

    def find_dictionary_kanji(self, query: str) -> Optional[Kanji]:
        """Searches dictionary for a Kanji."""
        return self.dictionary.get_kanji(query)

    def find_dictionary_radical(self, radical_id: int) -> Optional[Radical]:
        """Searches dictionary for radical by radical_id."""
        return self.dictionary.get_radical_by_id(radical_id)

    def get_vocab_entry(
        self, vocab_query: str, generate_vocab_cards: bool = False
    ) -> tuple[list[VocabCard], list[str]]:
        """Reads the matching entries from database for the given vocab query.

        Parameters
        ----------
        vocab_query : str
            Query to search for.
        generate_vocab_cards : bool, optional
            If True, generates missing VocabCard from dictionary entry, by default False
        """
        # ids of the cards that were not found in the database
        new_cards: list[str] = []

        vocab_query = vocab_query.strip()
        vocab_entries = self.db.get_vocab_entries_by_key(vocab_query)
        if generate_vocab_cards:
            # we have to match the entries dictionary_id with ent_seq key
            dictionary_entries = self.find_dictionary_vocab_by_writing(vocab_query)
            logging.info(f"Found {dictionary_entries} entries for {vocab_query}")
            for dictionary_entry in dictionary_entries:
                logging.info(f"Adding vocab card {dictionary_entry}")
                if dictionary_entry.ent_seq not in [
                    entry.dictionary_id for entry in vocab_entries
                ]:
                    new_card = VocabCard(
                        dictionary_id=dictionary_entry.ent_seq,
                        writing=vocab_query,
                        readings=[
                            AnswerText(answer_text=reading)
                            for reading in dictionary_entry.reading_elements
                        ],
                        # TODO: review - why test_enabled
                        meanings=[
                            VocabularyMeaningEntry(
                                part_of_speech=meaning.part_of_speech,
                                meanings=[
                                    AnswerText(answer_text=meaning)
                                    for meaning in meaning.meanings
                                ],
                                test_enabled=True,
                            )
                            for meaning in dictionary_entry.meanings
                        ],
                    )
                    vocab_entries.append(new_card)
                    new_cards.append(new_card.card_id)

            if not dictionary_entries:
                dictionary_reading_entries = self.find_dictionary_vocab_by_reading(
                    vocab_query
                )
                for dictionary_entry in dictionary_reading_entries:
                    logging.info(
                        f"\nAdding vocab card found by reading: {dictionary_entry}"
                    )
                    if dictionary_entry.ent_seq not in [
                        entry.dictionary_id for entry in vocab_entries
                    ]:
                        vocab_entries.append(
                            VocabCard(
                                dictionary_id=dictionary_entry.ent_seq,
                                writing=vocab_query,
                                readings=[],  # reading is same as writing, so we don't need it
                                # TODO: review - why test_enabled?
                                meanings=[
                                    VocabularyMeaningEntry(
                                        part_of_speech=meaning.part_of_speech,
                                        meanings=[
                                            AnswerText(answer_text=meaning)
                                            for meaning in meaning.meanings
                                        ],
                                        test_enabled=True,
                                    )
                                    for meaning in dictionary_entry.meanings
                                ],
                                note=f"Import note: Found in dictionary by reading, kanji: {dictionary_entry.kanji_elements}",
                            )
                        )

            if not vocab_entries:
                logging.warning(f"Word {vocab_query} not found in dictionary")
                vocab_entries = [
                    VocabCard(
                        writing=vocab_query,
                        readings=[],
                        meanings=[],
                        note="Warning: Word not found in dictionary",
                    )
                ]

        logging.info(f"Found {len(vocab_entries)} entries for {vocab_query}")
        logging.warning(vocab_entries)
        return vocab_entries, new_cards

    def get_kanji_cards(
        self, kanji_text: str, generate_kanji_cards: bool = False
    ) -> tuple[list[KanjiCard], list[str]]:
        """Finds the kanji in the database for the given vocab query.

        Parameters
        ----------
        vocab_query : VocabCard
            Word to search kanji for.
        generate_kanji_cards : bool, optional
            If True, generates missing KanjiCard from dictionary entry, by default False
        """
        # ids of the cards that were not found in the database
        new_cards: list[str] = []
        kanji_entries = []
        for char in kanji_text:
            db_kanji = self.db.get_card_by_key(char, CardType.KANJI)
            if db_kanji:
                if not isinstance(db_kanji, KanjiCard):
                    raise ValueError(
                        f"Incorrect card type for kanji {char}, {db_kanji}"
                    )
                kanji_entries.append(db_kanji)
                continue
            if generate_kanji_cards:
                kanji = self.find_dictionary_kanji(char)
                if kanji:
                    meanings: list[AnswerText] = [
                        AnswerText(answer_text=meaning.strip())
                        for entry in kanji.meanings
                        for meaning in entry.split(",")
                    ]

                    new_card = KanjiCard(
                        writing=char,
                        dictionary_id=kanji.ucs_codepoint,
                        meanings=meanings,
                        on_readings=[
                            AnswerText(answer_text=reading)
                            for reading in kanji.readings.get("ja_on", [])
                        ],
                        kun_readings=[
                            AnswerText(answer_text=reading)
                            for reading in kanji.readings.get("ja_kun", [])
                        ],
                        radical_id=kanji.radicals.get("classical", None),
                    )
                    kanji_entries.append(new_card)
                    new_cards.append(new_card.card_id)
                # else:
                #     logging.warning(f"Kanji {char} not found in dictionary")
                #     kanji_entries.append(
                #         KanjiCard(
                #             character=char,
                #             meanings=[],
                #             on_readings=[],
                #             kun_readings=[],
                #             note="Warning: Kanji not found in dictionary",
                #             radical_id=None,
                #         )
                #     )

        return kanji_entries, new_cards

    def get_radical_card(
        self, kanji: KanjiCard, generate_radical_cards: bool = False
    ) -> tuple[Optional[RadicalCard], list[str]]:
        """Generates radical card for Kanji."""
        """Finds the radical in the database for the given kanji.

        Parameters
        ----------
        kanji : KanjiCard
            Word to search radical for.
        generate_radical_cards : bool, optional
            If True, generates missing RadicalCard from dictionary entry, by default False

        Raises
        ------
        ValueError
            If kanji is not one character long
        """
        # ids of the cards that were not found in the database
        new_cards: list[str] = []

        # there can be only one radical for one kanji

        if kanji.radical_id is None:
            logging.warning(f"Kanji {kanji.writing} has no radical")
            return None, new_cards
        dict_radical = self.find_dictionary_radical(kanji.radical_id)
        if not dict_radical:
            logging.warning(f"Radical for kanji {kanji.writing} not found")
            # return RadicalCard(
            #     dictionary_id=kanji.radical_id,
            #     character="",
            #     meanings=[],
            #     reading="",
            #     note="Warning: Radical not found in dictionary",
            # )
            return None, new_cards
        db_radical = self.db.get_card_by_key(dict_radical.radical, CardType.RADICAL)
        if db_radical:
            if not isinstance(db_radical, RadicalCard):
                raise ValueError(
                    f"Incorrect card type for radical {dict_radical.radical}, {db_radical}"
                )
            return db_radical, new_cards
        if generate_radical_cards:
            new_card = RadicalCard(
                dictionary_id=dict_radical.id,
                writing=dict_radical.radical,
                meanings=[
                    AnswerText(answer_text=meaning.strip())
                    for meaning in dict_radical.meaning.split(",")
                ],
                reading=dict_radical.reading_j,
            )
            new_cards.append(new_card.card_id)
            return new_card, new_cards

        logging.warning(f"Radical for kanji {kanji.writing} not found")
        return None, new_cards

    def generate_kanji_import(
        self, kanji_list: str, existing_cards: Optional[list[TestCardTypes]] = None
    ) -> GeneratedImports:
        """Generates Kanji cards for a list."""
        logging.info(f"Generating import for kanji list: {kanji_list}")
        # ids of the generated cards in order and with dependencies
        import_items: list[ImportItem] = []
        generated_cards: dict[str, TestCardTypes] = {}
        errors: list[str] = []
        new_card_ids: list[str] = []

        if not existing_cards:
            existing_cards = []

        existing_kanji_cards: dict[int, KanjiCard] = {
            card.dictionary_id: card
            for card in existing_cards
            if isinstance(card, KanjiCard)
            if card.dictionary_id is not None
        }
        existing_radiacal_cards: dict[int, RadicalCard] = {
            card.dictionary_id: card
            for card in existing_cards
            if isinstance(card, RadicalCard)
            if card.dictionary_id is not None
        }

        if not kanji_list:
            raise ValueError("Empty kanji list")

        # remove newlines and spaces
        kanji_list = kanji_list.replace("\n", "").replace(" ", "")

        for kanji in kanji_list:
            kanji_cards, new_cards = self.get_kanji_cards(
                kanji, generate_kanji_cards=True
            )
            new_card_ids.extend(new_cards)

            if not kanji_cards:
                # will mostly show up when there is kana
                # TODO: add kana detection and skip
                logging.warning(f"Kanji '{kanji}' not found in dictionary")
                errors.append(f"Kanji '{kanji}' not found in dictionary")
                continue

            for kanji_card in kanji_cards:

                # check if the kanji is already imported
                if kanji_card.dictionary_id in existing_kanji_cards:
                    logging.info(
                        f"Kanji {kanji_card.writing} already imported, replacing"
                    )
                    if kanji_card.card_id in new_card_ids:
                        new_card_ids.remove(kanji_card.card_id)
                    kanji_card = existing_kanji_cards[kanji_card.dictionary_id]
                else:
                    if kanji_card.dictionary_id is None:
                        error_msg = f"Kanji {kanji_card.writing} has no dictionary id"
                        logging.warning(error_msg)
                        errors.append(error_msg)
                        continue

                    existing_kanji_cards[kanji_card.dictionary_id] = kanji_card

                generated_cards[kanji_card.card_id] = kanji_card
                kanji_import_item = ImportItem(item_id=kanji_card.card_id)

                radical_card, new_radical_cards = self.get_radical_card(
                    kanji_card, generate_radical_cards=True
                )
                new_card_ids.extend(new_radical_cards)
                if not radical_card:
                    logging.warning(
                        f"Radical for kanji {kanji} not found in dictionary"
                    )
                    errors.append(f"Radical for kanji {kanji} not found in dictionary")
                    continue

                # check if the radical is already imported
                if radical_card.dictionary_id in existing_radiacal_cards:
                    logging.info(
                        f"Radical {radical_card.writing} already imported, replacing"
                    )
                    if radical_card.card_id in new_card_ids:
                        new_card_ids.remove(radical_card.card_id)
                    radical_card = existing_radiacal_cards[radical_card.dictionary_id]
                else:
                    generated_cards[radical_card.card_id] = radical_card
                kanji_import_item.sub_items.append(
                    ImportItem(item_id=radical_card.card_id)
                )

                import_items.append(kanji_import_item)

        logging.info(f"Generated {len(generated_cards)} cards for kanji")
        return GeneratedImports(
            import_items=import_items,
            generated_cards=generated_cards,
            new_card_ids=new_card_ids,
            errors=errors,
        )

    def generate_vocab_import(
        self, vocab_list: list[str], source_id: str = ""
    ) -> GeneratedImports:
        """Generates cards from a vocabulary list."""
        # ids of the generated cards in order and with dependencies
        import_items: list[ImportItem] = []
        generated_cards: dict[str, TestCardTypes] = {}
        errors: list[str] = []
        new_card_ids: list[str] = []

        existing_vocab_cards: dict[int, VocabCard] = {}

        if not vocab_list:
            raise ValueError("Empty vocab list")

        for vocab in vocab_list:

            if vocab.startswith("#"):
                logging.info(f"Skipping comment: {vocab}")
                continue

            # get notes if there are any
            vocab, note = vocab.split("-", maxsplit=1) if "-" in vocab else (vocab, "")
            # remove whitespace
            vocab = vocab.strip()
            note = note.strip()

            # remove newlines - there should be none, but just in case
            vocab = vocab.replace("\n", "")
            vocab = vocab.replace("\r", "")

            if vocab == "":
                logging.info("Empty word in vocab list")
                continue

            vocab_cards, new_cards = self.get_vocab_entry(
                vocab, generate_vocab_cards=True
            )
            new_card_ids.extend(new_cards)

            if not vocab_cards:
                logging.warning(f"Vocab '{vocab}' not found in dictionary")
                errors.append(f"Vocab '{vocab}' not found in dictionary")
                continue

            for vocab_card in vocab_cards:
                vocab_card.note = note + "\n" + vocab_card.note
                if vocab_card.dictionary_id in existing_vocab_cards:
                    # skip if the vocab card is already imported
                    # in case the word is in the list multiple times
                    logging.info(
                        f"Vocab {vocab_card.writing} already imported, skipping"
                    )
                    continue
                else:
                    if vocab_card.dictionary_id is None:
                        error_msg = f"Vocab {vocab_card.writing} has no dictionary id"
                        logging.warning(error_msg)
                        errors.append(error_msg)
                    else:
                        existing_vocab_cards[vocab_card.dictionary_id] = vocab_card

                generated_cards[vocab_card.card_id] = vocab_card
                vocab_import_item = ImportItem(item_id=vocab_card.card_id)

                existing_cards = list(generated_cards.values())
                if vocab_card.writing:
                    generated_kanji_imports = self.generate_kanji_import(
                        vocab_card.writing, existing_cards=existing_cards
                    )
                    generated_cards.update(generated_kanji_imports.generated_cards)
                    new_card_ids.extend(generated_kanji_imports.new_card_ids)
                    errors.extend(generated_kanji_imports.errors)
                    vocab_import_item.sub_items.extend(
                        generated_kanji_imports.import_items
                    )

                import_items.append(vocab_import_item)

        logging.info(f"Generated {len(generated_cards)} cards for vocab")
        return GeneratedImports(
            import_items=import_items,
            generated_cards=generated_cards,
            new_card_ids=new_card_ids,
            errors=errors,
        )

    def import_cards(
        self, import_data: GeneratedImports, sources: list[CardSource]
    ) -> None:
        """Imports cards."""
        logging.info(f"Importing cards: {import_data}")
        logging.info(f"Will attach sources: {sources}")
        cards_to_add: list[TestCardTypes] = []
        # TODO: update the import to avoid duplicate links and
        # switch the links back to CardSourceLink
        source_links_to_add: set[tuple[str, str]] = set()

        # we need to recursiverly iterate over the import items
        # and add the cards to the list in deepest first order
        # this is so the cards can be learned in the correct order:
        # first the radicals, then the kanji, then the vocab
        def add_cards_to_list(import_item: ImportItem) -> None:
            for sub_item in import_item.sub_items:
                add_cards_to_list(sub_item)
            card = import_data.generated_cards[import_item.item_id]

            # attach the source link to all cards
            for source in sources:
                source_links_to_add.add(
                    # CardSourceLink(card_id=card.card_id, source_id=source.source_id)
                    (card.card_id, source.source_id)
                )

            # only add the card if it is not already in the database
            if card.card_id not in import_data.new_card_ids:
                logging.info(f"Card {card} already imported")
                return

            # check if the card was already added to the list
            for added_card in cards_to_add:
                if added_card.card_id == card.card_id:
                    logging.info(f"Card {card} already in import list")
                    return

            # check the database for the card (in case the import is run multiple times)
            # TODO: rewrite to use batch query to remove existing cards
            #   to speed up the process
            db_card = self.db.get_card_by_key(card.writing, card.card_type)
            if db_card and db_card.card_id == card.card_id:
                logging.info(f"Card {card} already imported")
                return

            logging.info(f"Adding card {card} to import list")
            cards_to_add.append(card)

        for import_item in import_data.import_items:
            add_cards_to_list(import_item)

        # Batch insert cards and source links
        self.db.add_cards(cards_to_add)
        self.db.add_card_source_links(
            [
                CardSourceLink(card_id=link[0], source_id=link[1])
                for link in source_links_to_add
            ]
        )

    def save_test_session(self) -> None:
        """Stores current test session in a file."""
        if self.test_session is None:
            logging.info("No test session to save")
            return

        session_file = self.workdir / "test_session.json"

        if session_file.exists():
            session_file.rename(
                self.workdir
                / f"test_session_backup_{datetime.datetime.now().isoformat()}.json"
            )
            logging.warning("Old test session file found, renamed to backup")

        with session_file.open("w", encoding="utf-8") as f:
            f.write(json.dumps(self.test_session.model_dump(mode="json")))

        # keep at most 5 backups
        backup_files = sorted(
            self.workdir.glob("test_session_backup_*.json"), reverse=True
        )
        for backup_file in backup_files[5:]:
            backup_file.unlink()

    def load_test_session(self) -> None:
        """Loads test session from saved file."""
        session_file = self.workdir / "test_session.json"

        if not session_file.exists():
            # if there is no session file do nothing
            logging.info("No test session file found")
            return

        with session_file.open("r", encoding="utf-8") as f:
            session_data = json.load(f)

        self.test_session = TestSession(db=self.db, **session_data)

    def clear_saved_test_session(self) -> None:
        """Deletes test session file."""
        session_file = self.workdir / "test_session.json"

        if session_file.exists():
            session_file.unlink()
            logging.info("Deleted test session file")
        else:
            logging.info("No test session file found")

    def get_num_upcoming_cards(self, num_days: int = 5) -> dict[int, int]:
        """Provides forecast for upcoming cards."""
        # 0 is today, 1 is tomorrow, etc.
        upcoming_by_date = datetime.datetime.now() + datetime.timedelta(days=1)
        # set the time to 0:00
        upcoming_by_date = upcoming_by_date.replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        upcoming_cards: dict[int, int] = {}
        num_last = self.get_num_due_cards(StartTestRequest())
        for days in range(num_days + 1):
            dt = datetime.timedelta(days=days)
            num_upcoming: int = self.db.get_num_due_by_date(upcoming_by_date + dt)
            upcoming_cards[days] = num_upcoming - num_last
            num_last = num_upcoming

        return upcoming_cards

    def get_num_recent_mistakes(self) -> dict[int, int]:
        """Provides counts of recent mistakes by day."""
        return self.db.mistakes_get_num_mistakes_by_day()
