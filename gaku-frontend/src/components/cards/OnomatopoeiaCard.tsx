import { MultiInput, MultiInputStr } from '../MultiInputComponent';
import { AnswerText, OnomatopoeiaCard } from '../../types/CardTypes';



const OnomatopoeiaEntryComponent: React.FC<{
    entry: OnomatopoeiaCard,
    onEntryChange: (entry: OnomatopoeiaCard) => void
}> = ({ entry, onEntryChange }) => {
    const handleChange = <K extends keyof OnomatopoeiaCard>(field: K, value: OnomatopoeiaCard[K]) => {
        onEntryChange({ ...entry, [field]: value });
    };

    const addDefinition = () => {
        const newDefinition = {
            meaning: { answer_text: "Meaning", required: false },
            equivalent: [{ answer_text: "Equivalent", required: false }]
        };
        onEntryChange({
            ...entry,
            definitions: [...entry.definitions, newDefinition]
        });
    };
    const removeDefinition = (index: number) => {
        const newDefinitions = entry.definitions.filter((_, i) => i !== index);
        onEntryChange({
            ...entry,
            definitions: newDefinitions
        });
    };
    const updateDefinitionEquivalent = (index: number, newEquivalent: AnswerText[]) => {
        const updatedEquivalentDefinitions = [...entry.definitions]
        updatedEquivalentDefinitions[index] = {
            ...updatedEquivalentDefinitions[index],
            equivalent: newEquivalent
        }
        onEntryChange({
            ...entry,
            definitions: updatedEquivalentDefinitions
        })
    }

    const updateDefinitionMeaning = (index: number, newMeaning: AnswerText) => {
        const updatedMeaningDefinition = [...entry.definitions]
        updatedMeaningDefinition[index] = {
            ...updatedMeaningDefinition[index],
            meaning: newMeaning
        };
        onEntryChange({
            ...entry,
            definitions: updatedMeaningDefinition
        })
    }

    return (
        <div>
            <p><b>Onomatopoeia</b>: <input type="text" value={entry.writing} onChange={(e) => handleChange('writing', e.target.value)} lang='en' /></p>
            <br />
            Kana writing:<br />
            <MultiInputStr
                values={entry.kana_writing}
                onChange={(newReadings) => handleChange('kana_writing', newReadings)}
                imeMode="toHiragana"
            />
            <br />
            {entry.definitions.map((definition, index) => (
                <div key={index}>
                    <b>Definition:</b><br />
                    Eqiuvalents:<br />
                    <MultiInput
                        values={definition.equivalent}
                        onChange={(newEquivalent) => updateDefinitionEquivalent(index, newEquivalent)}
                    />
                    <br />
                    Meaning:<br />
                    <input
                        type='text'
                        value={definition.meaning.answer_text}
                        onChange={(e) => updateDefinitionMeaning(index, { answer_text: e.target.value, required: definition.meaning.required })}
                        lang='en'
                    />
                    <input
                        type="checkbox"
                        checked={definition.meaning.required}
                        onChange={(e) => updateDefinitionMeaning(index, { required: e.target.checked, answer_text: definition.meaning.answer_text })}
                    />
                    {/* At least one definition is required */}
                    <button
                        onClick={() => removeDefinition(index)}
                        disabled={entry.definitions.length <= 1} >
                        Remove Definition
                    </button>

                    <br />
                </div>
            ))}
            <button onClick={addDefinition}>Add Definition</button>

            <br /><br />
            <div style={{ display: 'flex', flexDirection: 'row', gap: "1em", flexWrap: "wrap" }}>
                <div>
                    Note:<br />
                    <textarea value={entry.note ?? ''} onChange={(e) => handleChange('note', e.target.value)} />
                </div>
                <div>
                    Hint:<br />
                    <textarea value={entry.hint ?? ''} onChange={(e) => handleChange('hint', e.target.value)} />
                </div>
            </div>
        </div>
    );
};

export default OnomatopoeiaEntryComponent;