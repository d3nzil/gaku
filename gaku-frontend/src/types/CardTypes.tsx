// answer type enum
enum AnswerType {
    'ROMAJI' = 'ROMAJI',
    "HIRAGANA" = 'HIRAGANA',
    "KATAKANA" = 'KATAKANA',
    "KANA" = 'KANA',
};

interface AnswerText {
    answer_text: string;
    required: boolean;
}

interface Answer {
    answer_id: string;
    answer_type: AnswerType;
    header: string;
    header_num_questions: string;
    answers: AnswerText[];
    hint: string | null;
    note: string | null;
}

interface AnswerGroup {
    group_id: string;
    header: string;
    answers: Answer[];
}

interface TestQuestion {
    id: string;
    header: string;
    question: string;
    hint: string;
    answers: AnswerGroup[];
}

interface TestAnswer {
    // dictionary of question id to answer
    [key: string]: string;
}

interface CardSource {
    source_id: string;
    source_name: string;
    source_section: string;
}

interface VocabularyMeaningEntry {
    test_enabled: boolean;
    part_of_speech: string;
    meanings: AnswerText[];
}

enum CardType {
    "VOCABULARY" = "VOCABULARY",
    "KANJI" = "KANJI",
    "RADICAL" = "RADICAL",
    "QUESTION" = "QUESTION",
    "MULTI_CARD" = "MULTI_CARD",
    "ONOMATOPOEIA" = "ONOMATOPOEIA"
}

interface VocabEntry {
    card_id: string;
    custom_questions: TestQuestion[];
    note: string;
    hint: string;
    card_type: "VOCABULARY";
    dictionary_id: number | null;
    writing: string;
    reading_type: AnswerType;
    readings: AnswerText[];
    meanings: VocabularyMeaningEntry[];
}

interface KanjiEntry {
    card_id: string;
    dictionary_id: number | null;
    custom_questions: TestQuestion[];
    note: string;
    hint: string;
    card_type: "KANJI";
    writing: string;
    on_readings: AnswerText[];
    kun_readings: AnswerText[];
    meanings: AnswerText[];
    radical_id: number;
}

interface RadicalEntry {
    card_id: string;
    dictionary_id: number | null;
    custom_questions: TestQuestion[];
    note: string;
    hint: string;
    card_type: "RADICAL";
    writing: string;
    meanings: AnswerText[];
    reading: string;
}

interface QuestionEntry {
    card_id: string;
    note: string;
    hint: string;
    card_type: "QUESTION";
    question: string;
    answers: Answer[];
}

interface MultiCardEntry {
    // common fields
    card_id: string;
    note: string;
    hint: string;
    test_readings: boolean;
    test_meanings: boolean;

    // multi card specific fields
    card_type: "MULTI_CARD";
    multicard_type: "VOCABULARY" | "KANJI" | "RADICAL"
    card_ids: string[];
    cards: (VocabEntry | KanjiEntry | RadicalEntry)[];
    writing: string;
}

interface OnomatopoeiaDefinition {
    equivalent: AnswerText[];
    meaning: AnswerText;
}

interface OnomatopoeiaCard {
    // common fields
    card_id: string;
    note: string;
    hint: string;

    card_type: "ONOMATOPOEIA"
    writing: string;
    kana_writing: string[];
    definitions: OnomatopoeiaDefinition[];
}

interface KanjiInfo {
    [key: string]: KanjiEntry;
}

interface RadicalInfo {
    [key: string]: RadicalEntry;
}

interface ImportDataEntry {
    vocab: VocabEntry;
    kanji: KanjiInfo;
    radicals: RadicalInfo;
}

interface NextCardMessage {
    correct_answer: boolean;
    next_question: TestQuestion;
    test_card: VocabEntry | KanjiEntry | RadicalEntry | QuestionEntry | MultiCardEntry | OnomatopoeiaCard;
}

interface AnswerResult {
    answer_is_correct: boolean;
}

interface TestStatusMessage {
    questions_completed: number;
    questions_total: number;
    cards_completed: number;
    cards_total: number;
}

// new generated import format / types
interface ImportItem {
    // this contains the tree structure for the import data
    item_id: string;
    sub_items: ImportItem[];
}

interface GeneratedImports {
    // this contains the generated import data
    import_items: ImportItem[];
    // this contains the generated cards
    // dictionary - vocab, kanji or radical card
    generated_cards: {
        [key: string]: VocabEntry | KanjiEntry | RadicalEntry | QuestionEntry | MultiCardEntry | OnomatopoeiaCard;
    };
    new_card_ids: string[];
    errors: string[];
}

interface CardFilter {
    card_sources: CardSource[];
    card_types: CardType[];
    search_text: string;
    start_index: number | null;
    num_cards: number | null;
}

// extends CardFilter
interface StartTestRequest extends CardFilter {
    mark_answers: boolean;
    generate_extra_questions: boolean;
}


interface TestResults {
    total_cards: number;
    correct_responses: number;
    incorrect_responses: number;
    stats: string[]
}

export type {
    VocabEntry,
    AnswerText,
    VocabularyMeaningEntry,
    KanjiEntry,
    RadicalEntry,
    KanjiInfo,
    RadicalInfo,
    QuestionEntry,
    MultiCardEntry,
    OnomatopoeiaCard,
    ImportDataEntry,
    TestQuestion,
    TestAnswer,
    Answer,
    AnswerResult,
    CardSource,
    NextCardMessage,
    TestStatusMessage,
    ImportItem,
    GeneratedImports,
    CardFilter,
    StartTestRequest,
    TestResults,
};

export {
    AnswerType,
    CardType
};
