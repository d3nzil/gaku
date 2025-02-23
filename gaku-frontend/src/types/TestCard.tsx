enum AnswerType {
    KANA = 'KANA',
    ROMAJI = 'ROMAJI'
}

interface CardSource {
    id: number | null;
    source_name: string;
    source_section: string;
}

interface TestQuestion {
    id: number | null;
    question: string;
    answer_type: AnswerType;
    answers: string[];
    card_sources: CardSource[];
}

export type { TestQuestion as TestCard, AnswerType };