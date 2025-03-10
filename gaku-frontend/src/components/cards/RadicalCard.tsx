// import { AnswerType } from '../../types/CardTypes';
import { MultiInput } from '../MultiInputComponent';
import AnswerComponent from '../AnswerComponent';

type RadicalEntry = import('../../types/CardTypes').RadicalEntry;


const RadicalEntryComponent: React.FC<{
    entry: RadicalEntry,
    onEntryChange: (entry: RadicalEntry) => void
}> = ({ entry, onEntryChange }) => {
    const handleChange = (field: string, value: any) => {
        onEntryChange({ ...entry, [field]: value });
    };

    return (
        <div>
            <p><b>Radical</b>: <input type="text" value={entry.writing} onChange={(e) => handleChange('character', e.target.value)} lang='ja' /></p>
            Meanings:
            <MultiInput
                values={entry.meanings}
                onChange={(newMeanings) => handleChange('meanings', newMeanings)}
            />
            <br />
            Reading:<br />
            <input type="text" value={entry.reading} onChange={(e) => handleChange('reading', e.target.value)} />
            <br /><br />
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
            <br />
            Radical ID: {entry.dictionary_id}
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

export default RadicalEntryComponent;