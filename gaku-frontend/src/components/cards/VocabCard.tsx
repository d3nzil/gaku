import { AnswerType } from '../../types/CardTypes';
import { MultiInput } from '../MultiInputComponent';
import AnswerComponent from '../AnswerComponent';
import VocabularyMeaningComponent from '../VocabularyMeaningComponent';

type VocabEntry = import('../../types/CardTypes').VocabEntry;
type VocabularyMeaningEntry = import('../../types/CardTypes').VocabularyMeaningEntry;


const VocabEntryComponent: React.FC<{
    entry: VocabEntry,
    onEntryChange: (entry: VocabEntry) => void
}> = ({ entry, onEntryChange }) => {
    const handleChange = (field: string, value: any) => {
        onEntryChange({ ...entry, [field]: value });
    };

    const addMeaning = () => {
        const newMeaningEntry: VocabularyMeaningEntry = {
            part_of_speech: '',
            meanings: [],
            test_enabled: false
        };
        handleChange('meanings', [...entry.meanings, newMeaningEntry]);
    };

    const removeMeaning = (index: number) => {
        const newMeanings = [...entry.meanings];
        newMeanings.splice(index, 1);
        handleChange('meanings', newMeanings);
    };

    const updateMeaning = (index: number, updatedMeaningEntry: VocabularyMeaningEntry) => {
        const newMeanings = [...entry.meanings];
        newMeanings[index] = updatedMeaningEntry;
        handleChange('meanings', newMeanings);
    };

    return (
        <div>
            <p><b>Vocabulary</b>: <input type="text" value={entry.writing} onChange={(e) => handleChange('writing', e.target.value)} lang='ja' /></p>
            <p>
                <b>Reading Type</b>:
                <select
                    value={entry.reading_type}
                    onChange={(e) => handleChange('reading_type', e.target.value as AnswerType)}
                    className='react-select'
                >
                    {Object.values(AnswerType).map((type) => (
                        <option key={type} value={type}>
                            {type}
                        </option>
                    ))}

                </select>
            </p>
            Readings:
            <MultiInput
                values={entry.readings}
                onChange={(newReadings) => handleChange('readings', newReadings)}
                imeMode={
                    entry.reading_type === 'KATAKANA' ? 'toKatakana' :
                        entry.reading_type === 'HIRAGANA' ? 'toHiragana' :
                            null
                }
            />
            <br />
            <b>Meanings:</b><br /><br />
            {entry.meanings.map((meaning, index) => (
                <div key={index}>
                    <VocabularyMeaningComponent
                        meaning={meaning}
                        onMeaningChange={(updatedMeaning: VocabularyMeaningEntry) => updateMeaning(index, { ...meaning, meanings: updatedMeaning.meanings })}
                    />
                    <button onClick={() => removeMeaning(index)}>Remove Meaning</button>
                    <br />
                    <label>
                        Enable Testing
                        <input
                            type="checkbox"
                            checked={meaning.test_enabled}
                            onChange={(e) => {
                                updateMeaning(index, { ...meaning, test_enabled: e.target.checked });
                            }}
                        />
                    </label>
                    {/* <MultiInput
                        values={meaning.meaning.meanings}
                        onChange={(newMeanings) => updateMeaning(index, {
                            ...meaning,
                            meaning: { ...meaning.meaning, meanings: newMeanings }
                        })}
                    /> */}
                    <br /><br />
                </div>
            ))}
            <button onClick={addMeaning}>Add Meaning</button>
            <br />
            <div style={{ display: 'flex', flexDirection: 'row', gap: "1em", flexWrap: "wrap" }}>
                <div>
                    Note:<br />
                    <textarea value={entry.note || ''} onChange={(e) => handleChange('note', e.target.value)} />
                </div>
                <div>
                    Hint: <br />
                    <textarea value={entry.hint || ''} onChange={(e) => handleChange('hint', e.target.value)} />
                </div>
            </div>
            {/* Render custom questions */}
            {entry.custom_questions.map((question, index) => (
                <div key={index}>
                    <input
                        type="text"
                        value={question.question}
                        onChange={(e) => {
                            const newQuestions = [...entry.custom_questions];
                            newQuestions[index].question = e.target.value;
                            handleChange('custom_questions', newQuestions);
                        }}
                        placeholder="Custom Question"
                    />
                    {/* Use AnswerComponent */}
                    {question.answers.map((answer_group, group_idx) => {
                        return answer_group.answers.map((answer, idx) => (
                            <AnswerComponent
                                key={idx}
                                answer={answer}
                                onAnswerChange={(updatedAnswer) => {
                                    const newQuestions = [...entry.custom_questions];
                                    newQuestions[index].answers[group_idx].answers[idx] = updatedAnswer;
                                    handleChange('custom_questions', newQuestions);
                                }}
                            />
                        ))
                    })}
                </div>
            ))}
            Dictionary ID: {entry.dictionary_id}
        </div>
    );
};

export default VocabEntryComponent;