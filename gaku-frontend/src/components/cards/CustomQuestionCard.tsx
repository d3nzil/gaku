import { AnswerType } from '../../types/CardTypes';
import AnswerComponent from '../AnswerComponent';

type QuestionEntry = import('../../types/CardTypes').QuestionEntry;
type Answer = import('../../types/CardTypes').Answer;


const QuestionEntryComponent: React.FC<{
    entry: QuestionEntry;
    onEntryChange: (entry: QuestionEntry) => void;
}> = ({ entry, onEntryChange }) => {
    const handleChange = (field: keyof QuestionEntry, value: any) => {
        onEntryChange({ ...entry, [field]: value });
    };

    const updateAnswer = (index: number, updatedAnswer: Answer) => {
        const newAnswers = [...entry.answers];
        newAnswers[index] = updatedAnswer;
        handleChange('answers', newAnswers);
    };

    const addAnswer = () => {
        const newAnswers = [
            ...entry.answers,
            {
                id: '',
                answer_type: AnswerType.HIRAGANA,
                header: '',
                answers: [],
                hint: null,
                note: null,
            },
        ];
        handleChange('answers', newAnswers);
    };

    const removeAnswer = (index: number) => {
        const newAnswers = [...entry.answers];
        newAnswers.splice(index, 1);
        handleChange('answers', newAnswers);
    };

    return (
        <div>
            <p>
                <b>Question</b>:{' '}
                <input
                    type="text"
                    value={entry.question}
                    onChange={(e) => handleChange('question', e.target.value)}
                    placeholder="Question"
                />
            </p>
            {/* Render answers using AnswerComponent */}
            {entry.answers.map((answer, index) => (
                <div key={index}>
                    <AnswerComponent
                        answer={answer}
                        onAnswerChange={(updatedAnswer) => updateAnswer(index, updatedAnswer)}
                    />
                    <button onClick={() => removeAnswer(index)}>Remove Answer</button>
                </div>
            ))}
            <button onClick={addAnswer}>Add Answer</button>
            <br />
            Note:{' '}
            <textarea
                value={entry.note || ''}
                onChange={(e) => handleChange('note', e.target.value)}
                placeholder="Note"
            />
            Hint:{' '}
            <textarea
                value={entry.hint || ''}
                onChange={(e) => handleChange('hint', e.target.value)}
                placeholder="Hint"
            />
        </div>
    );
};

export default QuestionEntryComponent;