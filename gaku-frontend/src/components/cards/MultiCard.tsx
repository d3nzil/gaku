import React from 'react';
import { VocabEntry, KanjiEntry, RadicalEntry, CardType } from '../../types/CardTypes';
type MultiCardEntry = import('../../types/CardTypes').MultiCardEntry;


const MultiCardEntryComponent: React.FC<{
    entry: MultiCardEntry,
    onEntryChange: (entry: MultiCardEntry) => void
}> = ({ entry, onEntryChange }) => {
    const handleChange = (field: string, value: any) => {
        onEntryChange({ ...entry, [field]: value });
    };

    // multi card entry display structure
    // no field is editable as there is special editor for this card type
    // - question (writing) 
    // box containing the nested card entries 
    // - we display the writing of each card as it is available for all cards

    const getMeaning = (item: VocabEntry | KanjiEntry | RadicalEntry) => {
        if (item.card_type == CardType.VOCABULARY)
        {
            return (
                <p>Meanings:<br />
                    {item.meanings.map((vocabMeaning, idx) => (
                        <React.Fragment key={idx}>
                            {vocabMeaning.meanings.map(meaning => meaning.answer_text).join("; ")}
                            <br />
                        </React.Fragment>
                    ))}
                </p>
            )

        } else
        {
            return (<p>Meanings:<br />{item.meanings.map(item => item.answer_text).join("; ")}</p>)
        }

    }

    const getReading = (item: VocabEntry | KanjiEntry | RadicalEntry) => {
        if (item.card_type == CardType.VOCABULARY)
        {
            return (
                <p>Readings:<br />
                    <span lang='ja'>{item.readings.map(reading => reading.answer_text).join("; ")}</span>
                </p>
            )
        } else if (item.card_type == CardType.KANJI)
        {
            return (
                <p>
                    On readings: <span lang='ja'>{item.on_readings.map(reading => reading.answer_text).join("; ")}</span><br />
                    Kun readings: <span lang='ja'>{item.kun_readings.map(reading => reading.answer_text).join("; ")}</span>
                </p>
            )

        } else
        {
            return (<p>Reading:<br />{item.reading}</p>)
        }

    }

    return (
        <div>
            <p><b>Question</b>: <span lang='ja'>{entry.writing}</span></p>
            <p><b>Multicard type</b>: {entry.multicard_type}</p>
            {/* editable note and hint */}
            <b>Cards:</b>
            <div style={{ display: 'flex', flexDirection: 'row', gap: '0.5em', flexWrap: "wrap" }}>
                {entry.cards.map((card, index) => (
                    <div key={index} style={{ border: "1px solid grey", padding: "0.5em", borderRadius: "0.5em", minWidth: "10em" }}>
                        <p><b>{card.card_type}</b>:<br></br> <span lang='ja'>{card.writing}</span></p>
                        {getMeaning(card)}
                        {getReading(card)}
                        <input
                            type="button"
                            value="Delete"
                            onClick={() => {
                                const newCards = [...entry.cards];
                                newCards.splice(index, 1);
                                handleChange('cards', newCards);
                            }}
                        />
                    </div>
                ))}
            </div>
            <div style={{ display: 'flex', flexDirection: 'row', gap: '0.5em' }}>
                {/* checkboxes for test_readings and test_meanings */}
                <div>
                    <input
                        type="checkbox"
                        checked={entry.test_readings}
                        onChange={(e) => handleChange('test_readings', e.target.checked)}
                    />
                    <label>Test readings</label>
                </div>
                <div>
                    <input
                        type="checkbox"
                        checked={entry.test_meanings}
                        onChange={(e) => handleChange('test_meanings', e.target.checked)}
                    />
                    <label>Test meanings</label>

                </div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'row', gap: '1em', flexWrap: "wrap" }}>
                <div>
                    Note:<br />
                    <textarea value={entry.note || ''} onChange={(e) => handleChange('note', e.target.value)} />
                </div>
                <div>
                    Hint:<br />
                    <textarea value={entry.hint || ''} onChange={(e) => handleChange('hint', e.target.value)} />
                </div>
            </div>
        </div>
    );
}

export default MultiCardEntryComponent;



