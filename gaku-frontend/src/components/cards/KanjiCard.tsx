import { MultiInput } from '../MultiInputComponent';
import AnswerComponent from '../AnswerComponent';

type KanjiEntry = import('../../types/CardTypes').KanjiEntry;



const KanjiEntryComponent: React.FC<{
    entry: KanjiEntry,
    onEntryChange: (entry: KanjiEntry) => void
}> = ({ entry, onEntryChange }) => {
    const handleChange = (field: string, value: any) => {
        onEntryChange({ ...entry, [field]: value });
    };

    return (
        <div>
            <p><b>Kanji</b>: <input type="text" value={entry.writing} onChange={(e) => handleChange('character', e.target.value)} lang='ja' /></p>
            On Readings:
            <MultiInput
                values={entry.on_readings}
                onChange={(newReadings) => handleChange('on_readings', newReadings)}
                imeMode="toKatakana"
            />
            Kun Readings:
            <MultiInput
                values={entry.kun_readings}
                onChange={(newReadings) => handleChange('kun_readings', newReadings)}
                imeMode="toHiragana"
            />
            Meanings:
            <MultiInput
                values={entry.meanings}
                onChange={(newMeanings) => handleChange('meanings', newMeanings)}
            />
            <br />
            <div style={{ display: 'flex', flexDirection: 'row', gap: "1em", flexWrap: "wrap" }}>
                <div>

                    Note:<br />
                    <textarea value={entry.note || ''} onChange={(e) => handleChange('note', e.target.value)} />
                </div>
                <div>

                    Hint:<br />
                    <textarea value={entry.hint || ''} onChange={(e) => handleChange('hint', e.target.value)} />
                </div>
            </div>

            Dictionary ID: {entry.dictionary_id}
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
        </div>
    );
};

export default KanjiEntryComponent;