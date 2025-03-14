type VocabEntry = import('../../types/CardTypes').VocabEntry;
type KanjiEntry = import('../../types/CardTypes').KanjiEntry;
type RadicalEntry = import('../../types/CardTypes').RadicalEntry;
type QuestionEntry = import('../../types/CardTypes').QuestionEntry;
type MultiCardEntry = import('../../types/CardTypes').MultiCardEntry;
type OnomatopoeiaCard = import('../../types/CardTypes').OnomatopoeiaCard;

import VocabEntryComponent from './VocabCard';
import KanjiEntryComponent from './KanjiCard';
import RadicalEntryComponent from './RadicalCard';
import QuestionEntryComponent from './CustomQuestionCard';
import MultiCardEntryComponent from './MultiCard';
import OnomatopoeiaEntryComponent from './OnomatopoeiaCard';

const getEntryComponent = (
    entry: VocabEntry | KanjiEntry | RadicalEntry | QuestionEntry | MultiCardEntry | OnomatopoeiaCard,
    onEntryChange: (entry: VocabEntry | KanjiEntry | RadicalEntry | QuestionEntry | MultiCardEntry | OnomatopoeiaCard) => void
) => {
    switch (entry.card_type)
    {
        case 'VOCABULARY':
            return <VocabEntryComponent entry={entry as VocabEntry} onEntryChange={onEntryChange} />;
        case 'KANJI':
            return <KanjiEntryComponent entry={entry as KanjiEntry} onEntryChange={onEntryChange} />;
        case 'RADICAL':
            return <RadicalEntryComponent entry={entry as RadicalEntry} onEntryChange={onEntryChange} />;
        case 'QUESTION':
            return <QuestionEntryComponent entry={entry as QuestionEntry} onEntryChange={onEntryChange} />;
        case 'MULTI_CARD':
            return <MultiCardEntryComponent entry={entry as MultiCardEntry} onEntryChange={onEntryChange} />;
        case "ONOMATOPOEIA":
            return <OnomatopoeiaEntryComponent entry={entry as OnomatopoeiaCard} onEntryChange={onEntryChange} />;
        default:
            return null;
    }
};

export { getEntryComponent };

export default getEntryComponent;