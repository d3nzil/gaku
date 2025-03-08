"""Data for tests."""

from gaku.card_types import (
    VocabCard,
    KanjiCard,
    RadicalCard,
    VocabularyMeaningEntry,
    AnswerText,
)


VOCAB_CARD = VocabCard(
    card_id="vocab000-0feb-46fe-9a3d-5f1d81544bb8",
    dictionary_id=123654,
    note="vocab note",
    hint="vocab hint",
    writing="vocab writing",
    readings=[
        AnswerText(answer_text="lowercase vocab reading 1"),
        AnswerText(answer_text="MiXedCaSe vocab reading 2"),
    ],
    meanings=[
        VocabularyMeaningEntry(
            part_of_speech="part vocab",
            meanings=[
                AnswerText(answer_text="UPPERCASE VOCAB MEANING 1"),
                AnswerText(answer_text="Capitalised Vocab Meaning 2", required=True),
            ],
        )
    ],
)

KANJI_CARD = KanjiCard(
    card_id="kanji000-09f2-46d0-9783-f6a6518a83dc",
    writing="kanji writing",
    radical_id=987654,
    on_readings=[AnswerText(answer_text="kanji on reading")],
    kun_readings=[AnswerText(answer_text="kanji kun reading")],
    meanings=[AnswerText(answer_text="kanji meanings")],
)
RADICAL_CARD = RadicalCard(
    card_id="radical0-8a69-4406-87dc-92fcfcd1fcbc",
    writing="radical writing",
    reading="radical reading",
    meanings=[AnswerText(answer_text="radical meaning")],
)
