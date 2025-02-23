"""Dictionary files related functionality."""

from csv import DictReader
from pathlib import Path
from typing import Optional, List, Dict
import pydantic
import xml.etree.ElementTree as ET

# mypy: ignore-errors


class Radical(pydantic.BaseModel):
    """Dictionary Radical repesentation."""

    # the radical file is csv with the following columns:
    # Radical ID#,Stroke#,Radical,Meaning,Reading-J,Reading-R,R-Filename,Anim-Filename,Position-J,Position-R
    #  5,1,,diagonal sweeping stroke,のかんむり,nokanmuri,,,かんむり,kanmuri
    #  some entries have empty fields
    id: int
    stroke: Optional[int]
    radical: str
    meaning: str
    reading_j: str
    reading_r: Optional[str]
    position_j: Optional[str]
    position_r: Optional[str]


class RadicalDictionary:
    """Japanese radicals dictionary."""

    def __init__(self, src_file: Path) -> None:
        """Initialize radicals dictionary.

        Radicals are stored in a dictionary with radical as a key.
        """
        self._src_file = src_file
        self.radicals: dict[str, Radical] = {}

        self.load_radicals()

    def load_radicals(self) -> None:
        """Load radicals from the source csv file."""
        with open(self._src_file, "r", encoding="utf-8") as f:
            reader = DictReader(
                f,
                fieldnames=[
                    "id",
                    "stroke",
                    "radical",
                    "alternate",
                    "category",
                    "meaning",
                    "reading_j",
                    "reading_r",
                    "position_j",
                    "position_r",
                    "importance",
                    "frequency",
                    "examples",
                ],
            )
            # skip header
            next(reader)
            for row in reader:
                # print(row)
                # convert id, stroke to int
                row_id = int(row.pop("id"))
                if row["stroke"]:
                    try:
                        row_stroke = int(row.pop("stroke"))
                    except ValueError:
                        row_stroke = None
                radical = Radical(id=row_id, stroke=row_stroke, **row)
                self.radicals[radical.radical] = radical

    def get_radical(self, radical: str) -> Optional[Radical]:
        """Get radical by its name."""
        return self.radicals.get(radical)

    def get_radical_by_id(self, radical_id: int) -> Optional[Radical]:
        """Get radical by its ID."""
        for radical in self.radicals.values():
            if radical.id == radical_id:
                return radical
        return None


class Kanji(pydantic.BaseModel):
    """Kanji representation."""

    literal: str
    codepoints: Dict[str, str]
    ucs_codepoint: Optional[int]
    radicals: Dict[str, int]
    grade: Optional[int]
    stroke_count: List[int]
    variants: Dict[str, str]
    frequency: Optional[int]
    radical_names: List[str]
    jlpt: Optional[int]
    meanings: List[str]
    readings: Dict[str, List[str]]
    nanori: List[str]


class KanjiDictionary:
    """Japanese kanji dictionary."""

    def __init__(self, src_file: Path) -> None:
        """Initialize kanji dictionary.

        Kanji are stored in a dictionary with the literal character as a key.
        """
        self._src_file = src_file
        self.kanji: dict[str, Kanji] = {}

        self.load_kanji()

    def load_kanji(self) -> None:
        """Load kanji from the source XML file."""
        tree = ET.parse(self._src_file)
        root = tree.getroot()

        for character in root.findall("character"):
            literal = character.find("literal").text
            if not isinstance(literal, str):
                raise ValueError(f"Invalid literal: {literal}")
            codepoints = {
                cp.get("cp_type"): cp.text
                for cp in character.find("codepoint").findall("cp_value")
            }
            # convert UCS codepoint to int
            ucs_codepoint = codepoints.get("ucs", None)
            ucs_codepoint = (
                int(ucs_codepoint, base=16) if ucs_codepoint is not None else None
            )
            radicals = {
                rad.get("rad_type"): int(rad.text)
                for rad in character.find("radical").findall("rad_value")
            }
            grade = character.find("misc").find("grade")
            grade = int(grade.text) if grade is not None else None
            stroke_count = [
                int(sc.text) for sc in character.find("misc").findall("stroke_count")
            ]
            variants = {
                var.get("var_type"): var.text
                for var in character.find("misc").findall("variant")
            }
            frequency = character.find("misc").find("freq")
            frequency = int(frequency.text) if frequency is not None else None
            radical_names = [
                rn.text for rn in character.find("misc").findall("rad_name")
            ]
            jlpt = character.find("misc").find("jlpt")
            jlpt = int(jlpt.text) if jlpt is not None else None
            meanings: list[str] = []
            readings: dict[str, list[str]] = {}
            reading_meaning = character.find("reading_meaning")
            if reading_meaning is not None:
                for rmgroup in reading_meaning.findall("rmgroup"):
                    for meaning in rmgroup.findall("meaning"):
                        lang = meaning.get("m_lang", "en")
                        # keep only English meanings
                        if lang == "en":
                            meanings.append(meaning.text)
                    for reading in rmgroup.findall("reading"):
                        r_type = reading.get("r_type")
                        if not isinstance(r_type, str):
                            raise ValueError(f"Invalid reading type: {r_type}")
                        if r_type not in readings:
                            readings[r_type] = []
                        readings[r_type].append(reading.text)
                nanori = [nanori.text for nanori in reading_meaning.findall("nanori")]
            else:
                nanori = []

            kanji = Kanji(
                literal=literal,
                codepoints=codepoints,
                ucs_codepoint=ucs_codepoint,
                radicals=radicals,
                grade=grade,
                stroke_count=stroke_count,
                variants=variants,
                frequency=frequency,
                radical_names=radical_names,
                jlpt=jlpt,
                meanings=meanings,
                readings=readings,
                nanori=nanori,
            )
            self.kanji[literal] = kanji

    def get_kanji(self, literal: str) -> Optional[Kanji]:
        """Get kanji by its literal character."""
        return self.kanji.get(literal)


# pos = part of speech
POS_MAPPINGS = {
    "adj-f": "noun or verb acting prenominally",
    "adj-i": "adjective (keiyoushi)",
    "adj-ix": "adjective (keiyoushi) - yoi/ii class",
    "adj-kari": "'kari' adjective (archaic)",
    "adj-ku": "'ku' adjective (archaic)",
    "adj-na": "adjectival nouns or quasi-adjectives (keiyodoshi)",
    "adj-nari": "archaic/formal form of na-adjective",
    "adj-no": "nouns which may take the genitive case particle 'no'",
    "adj-pn": "pre-noun adjectival (rentaishi)",
    "adj-shiku": "'shiku' adjective (archaic)",
    "adj-t": "'taru' adjective",
    "adv": "adverb (fukushi)",
    "adv-to": "adverb taking the 'to' particle",
    "aux": "auxiliary",
    "aux-adj": "auxiliary adjective",
    "aux-v": "auxiliary verb",
    "conj": "conjunction",
    "cop": "copula",
    "ctr": "counter",
    "exp": "expressions (phrases, clauses, etc.)",
    "int": "interjection (kandoushi)",
    "n": "noun (common) (futsuumeishi)",
    "n-adv": "adverbial noun (fukushitekimeishi)",
    "n-pr": "proper noun",
    "n-pref": "noun, used as a prefix",
    "n-suf": "noun, used as a suffix",
    "n-t": "noun (temporal) (jisoumeishi)",
    "num": "numeric",
    "pn": "pronoun",
    "pref": "prefix",
    "prt": "particle",
    "suf": "suffix",
    "unc": "unclassified",
    "v-unspec": "verb unspecified",
    "v1": "Ichidan verb",
    "v1-s": "Ichidan verb - kureru special class",
    "v2a-s": "Nidan verb with 'u' ending (archaic)",
    "v2b-k": "Nidan verb (upper class) with 'bu' ending (archaic)",
    "v2b-s": "Nidan verb (lower class) with 'bu' ending (archaic)",
    "v2d-k": "Nidan verb (upper class) with 'dzu' ending (archaic)",
    "v2d-s": "Nidan verb (lower class) with 'dzu' ending (archaic)",
    "v2g-k": "Nidan verb (upper class) with 'gu' ending (archaic)",
    "v2g-s": "Nidan verb (lower class) with 'gu' ending (archaic)",
    "v2h-k": "Nidan verb (upper class) with 'hu/fu' ending (archaic)",
    "v2h-s": "Nidan verb (lower class) with 'hu/fu' ending (archaic)",
    "v2k-k": "Nidan verb (upper class) with 'ku' ending (archaic)",
    "v2k-s": "Nidan verb (lower class) with 'ku' ending (archaic)",
    "v2m-k": "Nidan verb (upper class) with 'mu' ending (archaic)",
    "v2m-s": "Nidan verb (lower class) with 'mu' ending (archaic)",
    "v2n-s": "Nidan verb (lower class) with 'nu' ending (archaic)",
    "v2r-k": "Nidan verb (upper class) with 'ru' ending (archaic)",
    "v2r-s": "Nidan verb (lower class) with 'ru' ending (archaic)",
    "v2s-s": "Nidan verb (lower class) with 'su' ending (archaic)",
    "v2t-k": "Nidan verb (upper class) with 'tsu' ending (archaic)",
    "v2t-s": "Nidan verb (lower class) with 'tsu' ending (archaic)",
    "v2w-s": "Nidan verb (lower class) with 'u' ending and 'we' conjugation (archaic)",
    "v2y-k": "Nidan verb (upper class) with 'yu' ending (archaic)",
    "v2y-s": "Nidan verb (lower class) with 'yu' ending (archaic)",
    "v2z-s": "Nidan verb (lower class) with 'zu' ending (archaic)",
    "v4b": "Yodan verb with 'bu' ending (archaic)",
    "v4g": "Yodan verb with 'gu' ending (archaic)",
    "v4h": "Yodan verb with 'hu/fu' ending (archaic)",
    "v4k": "Yodan verb with 'ku' ending (archaic)",
    "v4m": "Yodan verb with 'mu' ending (archaic)",
    "v4n": "Yodan verb with 'nu' ending (archaic)",
    "v4r": "Yodan verb with 'ru' ending (archaic)",
    "v4s": "Yodan verb with 'su' ending (archaic)",
    "v4t": "Yodan verb with 'tsu' ending (archaic)",
    "v5aru": "Godan verb - -aru special class",
    "v5b": "Godan verb with 'bu' ending",
    "v5g": "Godan verb with 'gu' ending",
    "v5k": "Godan verb with 'ku' ending",
    "v5k-s": "Godan verb - Iku/Yuku special class",
    "v5m": "Godan verb with 'mu' ending",
    "v5n": "Godan verb with 'nu' ending",
    "v5r": "Godan verb with 'ru' ending",
    "v5r-i": "Godan verb with 'ru' ending (irregular verb)",
    "v5s": "Godan verb with 'su' ending",
    "v5t": "Godan verb with 'tsu' ending",
    "v5u": "Godan verb with 'u' ending",
    "v5u-s": "Godan verb with 'u' ending (special class)",
    "v5uru": "Godan verb - Uru old class verb (old form of Eru)",
    "vi": "intransitive verb",
    "vk": "Kuru verb - special class",
    "vn": "irregular nu verb",
    "vr": "irregular ru verb, plain form ends with -ri",
    "vs": "noun or participle which takes the aux. verb suru",
    "vs-c": "su verb - precursor to the modern suru",
    "vs-i": "suru verb - included",
    "vs-s": "suru verb - special class",
    "vt": "transitive verb",
    "vz": "Ichidan verb - zuru verb (alternative form of -jiru verbs)",
}


class VocabularyMeaning(pydantic.BaseModel):
    """Vocabulary meaning representation."""

    # part of speech - pos in JMdict
    part_of_speech: str
    meanings: List[str]


class DictionaryEntry(pydantic.BaseModel):
    """Dictionary entry representation."""

    ent_seq: int
    kanji_elements: List[str]
    reading_elements: List[str]
    meanings: List[VocabularyMeaning]


class JapaneseDictionary:
    """Japanese dictionary loaded from JMdict_e.xml."""

    def __init__(self, src_file: Path) -> None:
        """Initialize the Japanese dictionary."""
        self._src_file = src_file
        self.entries: Dict[int, DictionaryEntry] = {}

        self.load_entries()

    def load_entries(self) -> None:
        """Load entries from the JMdict_e.xml file."""
        tree = ET.parse(self._src_file)
        root = tree.getroot()

        for entry in root.findall("entry"):
            ent_seq = int(entry.find("ent_seq").text)
            kanji_elements = [ke.find("keb").text for ke in entry.findall("k_ele")]
            if not isinstance(kanji_elements, list):
                if kanji_elements is None:
                    kanji_elements = []
                else:
                    raise ValueError(f"Invalid kanji elements: {kanji_elements}")
            reading_elements = [re.find("reb").text for re in entry.findall("r_ele")]
            if not isinstance(reading_elements, list):
                if reading_elements is None:
                    reading_elements = []
                else:
                    raise ValueError(f"Invalid reading elements: {reading_elements}")
            meanings = []
            for sense in entry.findall("sense"):
                pos_elements = [pos.text for pos in sense.findall("pos")]
                pos = pos_elements[0]
                glosses = [gloss.text for gloss in sense.findall("gloss")]
                if not glosses:
                    raise ValueError("No glosses found in sense")
                vm = VocabularyMeaning(part_of_speech=pos, meanings=glosses)
                meanings.append(vm)

            dictionary_entry = DictionaryEntry(
                ent_seq=ent_seq,
                kanji_elements=kanji_elements,
                reading_elements=reading_elements,
                meanings=meanings,
            )
            self.entries[ent_seq] = dictionary_entry

    def get_entry(self, ent_seq: int) -> Optional[DictionaryEntry]:
        """Get a dictionary entry by its sequence number."""
        return self.entries.get(ent_seq)

    def get_vocabulary_by_kanji(self, kanji: str) -> list[DictionaryEntry]:
        """Get a list of dictionary entries by their kanji."""
        return [
            entry for entry in self.entries.values() if kanji in entry.kanji_elements
        ]

    def get_vocabulary_by_reading(self, reading: str) -> list[DictionaryEntry]:
        """Get a list of dictionary entries by their reading."""
        return [
            entry
            for entry in self.entries.values()
            if reading in entry.reading_elements
        ]

    def get_vocabulary_by_meaning(self, meaning: str) -> list[DictionaryEntry]:
        """Get a list of dictionary entries by their gloss."""
        return [
            entry
            for entry in self.entries.values()
            for sense in entry.meanings
            if meaning.casefold() in sense["glosses"]
        ]


if __name__ == "__main__":
    radical_dict = RadicalDictionary(Path("resources/kanji-radicals.csv"))
    # print(radical_dict.radicals)
    kanji_dict = KanjiDictionary(Path("resources/kanjidic2.xml"))
    # print(kanji_dict.kanji)
    japanese_dict = JapaneseDictionary(Path("resources/JMdict_e.xml"))
    # print(japanese_dict.entries)
    # entries = japanese_dict.get_entries_by_kanji("日本")
    entries = japanese_dict.get_vocabulary_by_kanji("日")
    # entries = japanese_dict.get_entries_by_kanji("隙あり")
    # entries = japanese_dict.get_entries_by_reading("にほん")
    # entries = japanese_dict.get_entries_by_meaning("Japan")
    for entry in entries:
        print()
        print(f"Vocabulary: {entry}")

        for kanji in entry.kanji_elements:
            for character in kanji:
                kanji_entry = kanji_dict.get_kanji(character)
                # print("kanji: ", kanji_entry)
                if kanji_entry:
                    print(f"Kanji: {kanji_entry} radicals: ", kanji_entry.radicals)

                    if "classical" in kanji_entry.radicals:
                        radical = radical_dict.get_radical_by_id(
                            kanji_entry.radicals["classical"]
                        )
                        print("Radical: ", radical)
