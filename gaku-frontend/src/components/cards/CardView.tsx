type VocabEntry = import('../../types/CardTypes').VocabEntry;
type KanjiEntry = import('../../types/CardTypes').KanjiEntry;
type RadicalEntry = import('../../types/CardTypes').RadicalEntry;
type QuestionEntry = import('../../types/CardTypes').QuestionEntry;
type MultiCardEntry = import('../../types/CardTypes').MultiCardEntry;

import VocabEntryComponent from './VocabCard';
import KanjiEntryComponent from './KanjiCard';
import RadicalEntryComponent from './RadicalCard';
import QuestionEntryComponent from './CustomQuestionCard';
import MultiCardEntryComponent from './MultiCard';

const getEntryComponent = (
    entry: VocabEntry | KanjiEntry | RadicalEntry | QuestionEntry | MultiCardEntry,
    onEntryChange: (entry: VocabEntry | KanjiEntry | RadicalEntry | QuestionEntry | MultiCardEntry) => void
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
        default:
            return null;
    }
};

export { getEntryComponent };

export default getEntryComponent;