// AnswerComponent.tsx
import React from 'react';
import { AnswerType } from '../types/CardTypes';

type Answer = import('../types/CardTypes').Answer;

const AnswerComponent: React.FC<{
    answer: Answer;
    onAnswerChange: (updatedAnswer: Answer) => void;
}> = ({ answer, onAnswerChange }) => {
    const handleFieldChange = (field: keyof Answer, value: any) => {
        onAnswerChange({ ...answer, [field]: value });
    };

    return (
        <div>
            Answer type:
            <select
                value={answer.answer_type}
                onChange={(e) => handleFieldChange('answer_type', e.target.value)}
                className='react-select'
            >
                {Object.values(AnswerType).map((type) => (
                    <option key={type} value={type}>
                        {type}
                    </option>
                ))}
            </select><br />
            <input
                type="text"
                value={answer.header}
                onChange={(e) => handleFieldChange('header', e.target.value)}
                placeholder="Header"
            />
            <input
                type="text"
                value={answer.answers.join(', ')}
                onChange={(e) => handleFieldChange('answers', e.target.value.split(', '))}
                placeholder="Answers (comma-separated)"
            />
            <br />
            <textarea
                value={answer.hint || ''}
                onChange={(e) => handleFieldChange('hint', e.target.value)}
                placeholder="Hint"
            />
            <textarea
                value={answer.note || ''}
                onChange={(e) => handleFieldChange('note', e.target.value)}
                placeholder="Note"
            />
        </div>
    );
};

export default AnswerComponent;
